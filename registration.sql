--
-- PostgreSQL database dump
--

-- Dumped from database version 15.6 (Debian 15.6-1.pgdg120+2)
-- Dumped by pg_dump version 15.6 (Debian 15.6-1.pgdg120+2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: registration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration (
    id integer NOT NULL,
    firstname character varying NOT NULL,
    lastname character varying NOT NULL,
    phonenumber character varying NOT NULL,
    email character varying NOT NULL,
    region character varying,
    locality character varying,
    district character varying,
    school character varying,
    classtype character varying,
    classstream character varying,
    test integer,
    university character varying,
    speciality character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.registration OWNER TO postgres;

--
-- Name: registration_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.registration_id_seq OWNER TO postgres;

--
-- Name: registration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registration_id_seq OWNED BY public.registration.id;


--
-- Name: registration id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration ALTER COLUMN id SET DEFAULT nextval('public.registration_id_seq'::regclass);


--
-- Data for Name: registration; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registration (id, firstname, lastname, phonenumber, email, region, locality, district, school, classtype, classstream, test, university, speciality, created_at) FROM stdin;
1	test	test	77026352452	danil6167@mail.ru	1	1	1	1	1	1	\N	{"9,5,7,6"}		2024-03-05 07:56:01.308646+00
2	test	test2	77076454853	test@mail.ru	1	1	1	1	1	1	6	\N	{"1,2,4"}	2024-03-13 09:43:10.637737+00
\.


--
-- Name: registration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registration_id_seq', 2, true);


--
-- Name: registration registration_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration
    ADD CONSTRAINT registration_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

