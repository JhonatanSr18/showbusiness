"""Create/reset a PostgreSQL admin without storing credentials in source.

Run interactively with DATABASE_URL configured, or use --from-env for a
short-lived Render start command. Remove ADMIN_SETUP_PASSWORD after use.
"""
import argparse
import getpass
import os
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-env", action="store_true")
    args = parser.parse_args()

    if args.from_env:
        password = os.environ.pop("ADMIN_SETUP_PASSWORD", "")
        if not password:
            print("ADMIN_SETUP_SKIPPED: no temporary secret configured.")
            return 0
    else:
        password = getpass.getpass("Nova senha do admin (minimo 16 caracteres): ")
        if password != getpass.getpass("Confirme a senha: "):
            print("ADMIN_SETUP_FAILED: passwords do not match.", file=sys.stderr)
            return 1

    if len(password) < 16:
        print("ADMIN_SETUP_FAILED: use at least 16 characters.", file=sys.stderr)
        return 1

    database_url = os.environ.get("DATABASE_URL", "")
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]

    try:
        from flask import Flask
        from sqlalchemy import text
        from sqlalchemy.engine import make_url
        from werkzeug.security import check_password_hash, generate_password_hash
        from models import db, Admin

        url = make_url(database_url)
        if url.get_backend_name() != "postgresql":
            print("ADMIN_SETUP_FAILED: PostgreSQL DATABASE_URL required.", file=sys.stderr)
            return 1
        if not url.host or not url.database:
            print("ADMIN_SETUP_FAILED: incomplete database configuration.", file=sys.stderr)
            return 1

        setup_app = Flask(__name__)
        setup_app.config.update(
            SQLALCHEMY_DATABASE_URI=url,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            SQLALCHEMY_ENGINE_OPTIONS={"hide_parameters": True},
        )
        db.init_app(setup_app)
        with setup_app.app_context():
            try:
                # Serialize concurrent setup attempts without changing the schema.
                db.session.execute(text(
                    "SELECT pg_advisory_xact_lock(734819, 1)"
                ))
                admin = Admin.query.filter_by(usuario="admin").first()
                if admin and check_password_hash(admin.senha_hash, password):
                    action = "unchanged"
                else:
                    action = "reset" if admin else "created"
                    if admin is None:
                        admin = Admin(usuario="admin")
                        db.session.add(admin)
                    admin.senha_hash = generate_password_hash(password)
                    if not check_password_hash(admin.senha_hash, password):
                        raise RuntimeError("Hash verification failed")
                db.session.commit()
                print("ADMIN_SETUP_OK: " + action + " in PostgreSQL.")
            except Exception:
                db.session.rollback()
                raise
            finally:
                db.session.remove()
                db.engine.dispose()
        return 0
    except Exception:
        # Never print exception details: database errors can include secrets.
        print("ADMIN_SETUP_FAILED: check database connectivity and admin schema.", file=sys.stderr)
        return 1
    finally:
        password = None


if __name__ == "__main__":
    raise SystemExit(main())
