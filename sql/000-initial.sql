
--- Create web user timeline
CREATE ROLE timeline;
ALTER ROLE timeline WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS ;

--- Create DBA role
CREATE ROLE timeline_dba;
ALTER ROLE timeline_dba WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS ;

CREATE TABLE deploy_releases
(
        version varchar(255),
        deployed_at timestamp default now()
);

ALTER TABLE deploy_releases OWNER TO timeline_dba;

GRANT SELECT ON deploy_releases TO timeline;

