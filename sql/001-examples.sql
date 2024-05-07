CREATE TABLE examples (
      id SERIAL NOT NULL,
      name VARCHAR(100) NOT NULL,
      PRIMARY KEY (id)
);

ALTER TABLE examples OWNER TO timeline;

INSERT INTO public.examples(id, name) VALUES(DEFAULT, 'foo');
INSERT INTO public.examples(id, name) VALUES(DEFAULT, 'bar');
INSERT INTO public.examples(id, name) VALUES(DEFAULT, 'baz');
