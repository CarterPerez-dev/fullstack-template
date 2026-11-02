.. ©AngelaMos | 2026
.. README.rst

Fullstack Templates
===================

Opinionated application starters, generated with one command. The same generator
uses a local checkout during development and individual versioned archives for
public distribution.

The coordinated release is in preparation. Application runtime checks, dependency
updates, remote synchronization, and hosted installation are still release gates.
See the `audit and verification record <docs/plans/2026-10-25-template-release-audit.md>`_.

Generate locally
----------------

Python 3.10 or newer is required. From this repository:

.. code-block:: bash

   just install
   template list

Then, from the directory where you keep projects:

.. code-block:: bash

   template fastapi-stack my-app
   cd my-app
   just

The local installation links to this checkout. Subsequent generations use its
current files. Generated projects are independent copies; their edits do not flow
back into the template automatically.

Available variants
------------------

* ``go``: Go API, PostgreSQL, Redis, ES256 authentication.
* ``fastapi``: FastAPI API, PostgreSQL, Redis, JWT authentication.
* ``open``: React and SCSS without authentication.
* ``frontend``: React authentication client for the FastAPI contract.
* ``native``: Expo authentication client for the FastAPI mobile contract.
* ``fastapi-stack``: FastAPI with its React client.
* ``go-stack``: Go with a React client adapted to its API contract.
* ``portfolio``: Editable portfolio with administration through an owner account.

The standalone clients accept an explicit backend endpoint:

.. code-block:: bash

   template frontend my-web --api-url https://api.example.com/api
   template native my-mobile --api-url https://api.example.com/api

Use the API base before ``/v1``. For a direct backend this is normally the origin;
the bundled web proxy exposes it under ``/api``.

Initialization
--------------

Generation creates separate production and development dotenv files, credentials,
high host ports, project identifiers, and ``.template.json`` provenance. It excludes
real environment files, signing keys, uploads, dependencies, and build artifacts.
Existing project files are never overwritten. An existing ``.git`` directory in
an otherwise empty destination is preserved.

Run application services through each project's Docker Compose setup. The Go
startup initializes a signing-key volume and applies checked migrations; Python
startup applies Alembic migrations. Use HTTPS for production authentication.

Public distribution
-------------------

The planned installer endpoint is ``https://angelamos.com/template/install.sh``.
It is not confirmed deployed. After publication, it installs the small
``template`` command; generation downloads only the requested stack archive.
Checksums and source revision metadata accompany each release.

See `generator and installer details <template-tool/README.md>`_ and
`operations and release instructions <docs/template-operations.md>`_.

Verification
------------

.. code-block:: bash

   just check-template
   python3 -B tests/release/check_generated.py go-stack development

The second command needs Docker and creates an isolated temporary project. It
builds and starts that project, checks readiness and proxy routing, then removes
only its own containers and volumes. CI covers all eight variants, PostgreSQL
security tests, dependency audits, web builds, and Expo export before packaging.
Configured CI gates are not evidence of a completed successful CI run.

The frontend starter uses restrained spacing, system typography, and functional
navigation. Its default screen provides no product branding or fabricated service
status. Portfolio retains its content editor and configurable presentation.

License
-------

See `LICENSE <LICENSE>`_.
