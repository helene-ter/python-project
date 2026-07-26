# Autocomplétion

## Execution

Dans ressources/application.ini, la variable nbWords permet de changer le nombre de mots en sortie voulu.
Pour lancer le service, effectuer les commandes suivantes :

    - docker build -t python-project .
    - docker run -p 8080:8080 python-project
    - Dans un navigateur, appeler l'endpoint : http://localhost:8080/search?query=[param]

### Construction de l'endpoint

Méthode : GET /search
Paramètre : @RequestParameter query
Retour : List<String> response

## Conception

### Choix arborescence 
Le but est de séparer les couches logiques en différents répertoires.

    - apis : tout ce qui touche à la requête
    - core : tout ce qui concerne la logique métier
    - ressources/application.ini : tout ce qui concerne les paramètres applicatifs modifiables

### Choix du fonctionnement 

Le code suit le principe de la séparation des responsabilités. Chaque fonction a sa responsabilité :

    - Lire les fichiers
    - Ordonner les mots par ordre alphabétique
    - Définir et traiter les requêtes HTTP sur le serveur défini

Si query est vide, ou si aucun mot des fichiers sources ne commence par la valeur recherchée, la liste renvoyée sera vide, sans retour d'erreur. Dans le cas d'une autocomplétion, l'utilisateur n'a pas besoin de savoir autre chose que le fait qu'aucun résultat n'a été trouvé. Ce type de gestion de liste vide relève d'un comportement utilisateur, donc à gérer côté front.

### Choix de developpement 

Pour que le programme ne dépende pas des noms de fichiers, le plus simple est de tout lire d'un coup et de tout stocker dans une liste. Nous n'avons alors que des opérations à complexité linéaire.

Si le programme dépendait du nom des fichiers, alors, si l'on souhaitait plus tard en ajouter un, il faudrait faire évoluer le code, tout relancer et redéployer, entraînant ainsi une rupture temporaire de service.

L'avantage est qu'une fois la liste triée, il suffit de prendre les nbWords premiers éléments correspondant à la recherche, sans avoir à recroiser plusieurs sources de données.


#### Pourquoi tout stocker dans une liste ? 

Une liste simple est suffisante, la fonction de tri n'a pas besoin de connaître l'origine des mots (un seul dico ou plusieurs), elle reçoit une seule collection de mots à traiter, en une seule opération. Cela évite de complexifier la méthode avec une logique de fusion ou d'itération sur plusieurs sources.
Le même principe s'applique à do_get : la recherche se fait sur une liste déjà consolidée, sans qu'elle ait à savoir combien de fichiers ont contribué à la construire.

#### Pourquoi un GET ?

Le paramètre passé est un simple caractère, ce n'est pas un objet personnalisé ; si cela avait été le cas, un POST pour /search aurait été plus adapté.

Il n'y a pas de logique métier dans l'exécution de la requête, ni d'impact sur les fichiers : il s'agit uniquement d'une récupération de ressource.

# Extension architecture 
# Extension architecture

## Scénario 1 : on souhaite ajouter un front-end à notre application : quelle techno ? Pourquoi ? À quoi faut-il penser ?

### Choix de la technologie

**Quelle techno ?**

HTML / CSS / JS sans framework.

**Pourquoi ?**

On dispose d'une seule fonctionnalité : il n'y a ni navigation de pages, ni logique métier complexe.

Construire le code via Angular ou React pourrait avoir des avantages :
- Angular dispose d'une bibliothèque de composants avec Angular Material - Autocomplete, dont la documentation est bonne pour l'adapter et l'utiliser. On évite l'implémentation du style, il suffit d'utiliser la balise HTML Angular Material pour l'obtenir.
- Router l'application.
- Avoir une gestion uniformisée grâce au fonctionnement par composants.

Cependant, si aucune évolution n'est prévue, on s'ajoute de la difficulté : initialiser le projet, se perdre dans l'arborescence native du framework. On aurait aussi une charge de maintenance sur le projet, avec la gestion des dépendances pour éviter les problèmes de CVE.

**À quoi faut-il penser ?**

*Les utilisateurs de l'application*

Si l'application est destinée au public, alors, pour faciliter l'accès, il faut réfléchir à la sécurisation de la communication via un certificat signé par une autorité de certification, pour le navigateur — sinon l'utilisateur devra systématiquement valider que le site est sans risque.

*L'appel HTTP*

Met-on le front et le back sur le même serveur ? Ne pas le faire nous permet de mieux distinguer les logs en cas d'erreurs.

*L'accès aux données*

On peut vouloir catégoriser l'accès aux données, en réglementant la recherche des utilisateurs sur certains fichiers. Si c'est le cas, côté back, on pourrait mettre en place un système d'habilitation des utilisateurs.

*L'authentification*

Le front va gérer la connexion, mais le back va gérer la vérification de l'authentification, ce qui nous donnerait la possibilité d'inclure des droits dans le token, par exemple via Entra ID.

## Scénario 2 : on souhaite sauvegarder les recherches faites par les utilisateurs pour pouvoir les analyser : quelle techno ? Pourquoi ? À quoi faut-il penser / faire attention ?

**Quelle techno ?**

Elasticsearch, couplé à Kibana pour la visualisation.

**Pourquoi ?**

Visualiser ces données nativement via Kibana, son outil de dashboard associé.
Gérer les accès au niveau du serveur lui-même : les utilisateurs et leurs rôles sont définis dès la mise en place du cluster, ce qui centralise le contrôle d'accès plutôt que de le gérer dans chaque application cliente.

Pour une solution plus légère, les API Google Sheets permettent de stocker des données en petite quantité.

**À quoi faut-il penser ?**

*Contrôle d'accès à l'analyse*

Restreindre l'accès aux données à des utilisateurs appartenant à un groupe défini, plutôt qu'à tout le monde par défaut.
Stocker les identifiants de connexion (compte de service applicatif) dans un gestionnaire de secrets, jamais dans un fichier de configuration en clair.

*Plan de continuité d'activité*

Prévoir une stratégie de sauvegarde régulière des données du cluster, pour pouvoir toujours analyser l'historique même en cas d'incident.
Définir une politique de rétention claire : combien de temps conserver les données, et quelle volumétrie cela représente dans la durée.

*Fiabilité des écritures concurrentes*

Anticiper les pics d'écriture simultanée (plusieurs utilisateurs qui recherchent en même temps, ou plusieurs sauvegardes poussées en parallèle) : vérifier que le dimensionnement des pools de connexion à la base est suffisant, et s'assurer qu'aucune donnée ne soit écrasée par une écriture concurrente mal ordonnancée.

## Scénario 3 : ton équipe reçoit un ticket d'un bug utilisateur : erreur 500 lorsque l'utilisateur entre "coucou (sourire)" (l'emoji est important) : que faites-vous ? À quoi cela vous fait-il penser ?

**Que faites-vous ?**

1. Regarder la stack trace du serveur back : une erreur 500 signifie que le serveur n'a pas su gérer l'entrée et a levé une erreur.
2. Reproduire le bug en local, avec la même entrée exacte, avant toute autre investigation, pour observer l'erreur dans un environnement contrôlé.
3. Vérifier le trajet exact du paramètre avant qu'il n'arrive au code applicatif :
   - Le paramètre est-il transmis en string (URL) ou en body JSON ? Les deux ont des règles d'encodage différentes, et un emoji dans une URL implique un encodage particulier qui peut être mal géré selon les couches applicatives appelées pour le traitement.
   - Le paramètre transite-t-il par un WAF imposant des règles de sécurité ? Si oui, il est possible que ces règles, pensées pour détecter des tentatives d'injection SQL, réagissent à l'encodage inhabituel d'un emoji et le bloquent par erreur. Dans ce cas, la stack trace applicative ne montrerait rien d'anormal, puisque le blocage aurait lieu avant d'atteindre le back : il faudrait alors consulter les logs du WAF/proxy lui-même, séparés des logs applicatifs.