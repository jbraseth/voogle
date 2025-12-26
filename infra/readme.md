# 🎧 Voilib Deployment
This folder contains all the infrastructure code needed to run
**Voilib**.  It uses some Docker-based services configured with a
`Docker Compose` file (different in development and in production).

> The main commands to build and run all the needed services are in
> the provided [makefile](./makefile). Run `make` from [infra/
> folder](./) to see all of them (although you should read all this
> guide first).

## In development mode...
In development mode (see [development/ folder](./development))
frontend and backend code is using a [bind
mount](https://docs.docker.com/storage/bind-mounts/) so that you don't
need to rebuild the `Docker` images every time you change something in
the code.

- The [compose.yml](./development/compose.yml) file expects a
`.env` file in the [./development/](./development) folder with the
needed environment variables.  **You should create it before building
any service**, you can copy the provided
[.env.example](./development/.env.example).

▶️ When the `.env` file is created, you can build the Docker images
for all the services with `make dev-build` (it performs a `docker
compose build`) and run all of them with `make dev-run` (it performs a
`docker compose up`). The following services will be available:

- Application **frontend** at [http://localhost](http://localhost)
  (although it won't be ready yet for queries)
- **Management Dashboard** at [http://localhost:8501](http://localhost:8501)
- **REST API** at [http://localhost:81/service/](http://localhost:81/service/)
  with  `Swagger` docs at
  [http://localhost:81/service/docs](http://localhost:81/service/docs)
- `Qdrant` (vector database) running at [http://qdrant:6333](http://qdrant:6333)
  (from the internal Docker network)

ℹ️ Now read [first-run tasks section](#first-run-tasks) to find how to
 configure and start adding content to the application.

## In production...
- As in development (read [that section](#in-development-mode) first),
**you must create a `.env` file** in the
[./production/](./production) folder from the provided example:
[.env.example](./production/.env.example)

- When you do it, ensure to use your own domain in `VITE_API_HOST`.
Replace it also in the following lines from the `compose.yml` file
(you can search and replace `voilib.com` in the file):

```yaml
- "traefik.http.routers.ui.rule=(Host(`voilib.com`) && PathPrefix(`/`))"
```

 ```yaml
 - "traefik.http.routers.api.rule=(Host(`voilib.com`) && PathPrefix(`/service`))"
 ```

 ...and


```yaml
- "traefik.http.routers.management.rule=(Host(`voilib.com`) && PathPrefix(`/management`))"
```

-  There are also some references to `voilib.com` in
 [traefik.prod.toml](./production/traefik.prod.toml) that you should
 replace with your own domain.

-  You should change the default `SECRET_KEY` provided in
 [.env.example](./production/.env.example) by running the
 suggested command, and also the `ADMIN_PASSWORD`.

▶️ To build all the production images and run them, use `make prod-build`
and `make prod-run`.

ℹ️ Now read [first-run tasks section](#first-run-tasks) to find how to
 configure and start adding content to the application.

## First run tasks
The first time you run all the services you will need to perform the
following tasks.

###  💾 Running database migrations

> ℹ️ In Docker-based installations, Voilib will run migrations
> automatically from a Docker entrypoint. You can skip this step.

Voilib uses `sqlite` to store some information about podcasts and
episodes. To ensure the database file with all the needed tables is
created you should run the following command from [infra/ folder](./):

```bash
cd development && docker compose exec backend alembic upgrade head
```

...or this one in production:

```bash
cd production && docker compose exec backend alembic upgrade head
```


###  👤 Creating and admin user

> ℹ️ In Docker-based installations, Voilib will create automatically
> the admin user. By default, username will be `voilib-admin` and
> password `*audio*search*engine`, although they can be configured
> with environment variables. So, you can skip this step.


Open `Swagger` at and use the `/users/signup` endpoint to register a
new user. You can use whatever email or password you want but, to
ensure the user is automatically recognized as an admin, you should
use the username **`voilib-admin`**.

> ℹ️ There is a setting with the name `admin_username` to tell
> `FastAPI` the username we want to be automatically promoted to admin
> after sign-up.

There are some API endpoints that can be only used by admin users. You
can check all the available endpoint with `Swagger`.

###  🎧 Adding podcasts metadata

> ℹ️ This can be also done from **Voilib Management Dashboard**.
> From there, you can also add your own audio files to Voilib.

The file [urls.json](../backend/src/voilib/collection/urls.json)
contains the list of podcast that Voilib will collect. By default it
contains some examples of popular podcast. You can change this list
and add the feeds from all the podcasts you want. I usually use
[listennotes.com](https://www.listennotes.com) to find the URLs of the
RSS feeds of my favorite podcasts.

The following command (run it from from [infra/ folder](./)) will
start collecting episodes from all the configured feeds:

```bash
cd development && docker compose exec worker voilib-episodes --update
```

...or this one in production:


```bash
cd production && docker compose exec worker voilib-episodes --update
```

### 🕒 Configuring periodic collect/transcript/index jobs

> ℹ️ You can easily run these tasks from  **Voilib Management Dashboard**.

You can use `cron` to configure **periodic jobs** that will
**collect**, **transcript** and **index** new episodes. Here you have
my development configuration (assuming you work in Linux, run `crontab
-e` to modify `cron` configuration):

```bash
# update list of episodes every 6 hours
0 */6 * * * cd /{change-me}/voilib/infra/development && docker compose exec worker voilib-episodes --update

# transcribe last day episodes every 12 hours
20 */12 * * * cd /{change-me}/accushoot/voilib/infra/development && docker compose exec worker voilib-episodes --transcribe-days 1

# index pending episodes every 6 hours
40 */6 * * * cd /{change-me}/voilib/infra/development && docker compose exec worker voilib-episodes --store

```

...and my production configuration


```bash
# update list of episodes every 6 hours
0 */6 * * * cd /{change-me}/voilib/infra/production && docker compose exec worker voilib-episodes --update

# transcribe last day episodes every 12 hours
20 */12 * * * cd /{change-me}/accushoot/voilib/infra/production && docker compose exec worker voilib-episodes --transcribe-days 1

# index pending episodes every 6 hours
40 */6 * * * cd /{change-me}/voilib/infra/production && docker compose exec worker voilib-episodes --store
```

Don't forget to change all `/{change-me}` to the actual path that
contains the Voilib repository.
