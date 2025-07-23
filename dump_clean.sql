--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5 (Debian 17.5-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: empresas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresas (
    id integer NOT NULL,
    nome character varying(120) NOT NULL,
    cnpj character varying(20),
    endereco character varying(200),
    telefone character varying(20),
    contato character varying(100),
    email character varying(120),
    cidade character varying(80),
    estado character varying(2),
    cep character varying(10),
    criado_em timestamp without time zone
);


--
-- Name: empresas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresas_id_seq OWNED BY public.empresas.id;


--
-- Name: estados; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estados (
    id integer NOT NULL,
    sigla character varying(2) NOT NULL,
    nome character varying(80) NOT NULL
);


--
-- Name: estados_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estados_id_seq OWNED BY public.estados.id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    location_id character varying(200) NOT NULL,
    date_created timestamp without time zone
);


--
-- Name: municipios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.municipios (
    id integer NOT NULL,
    nome character varying(120) NOT NULL,
    estado_id integer
);


--
-- Name: municipios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.municipios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: municipios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.municipios_id_seq OWNED BY public.municipios.id;


--
-- Name: parceiros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parceiros (
    id integer NOT NULL,
    nome character varying(120) NOT NULL,
    telefone character varying(40),
    cidade character varying(80),
    uf character varying(2),
    cpf character varying(14),
    pix character varying(100),
    cep character varying(80),
    rua character varying(120),
    numero character varying(14),
    complemento character varying(40),
    bairro character varying(120)
);


--
-- Name: parceiros_empresas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parceiros_empresas (
    parceiro_id integer,
    empresa_id integer
);


--
-- Name: parceiros_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.parceiros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: parceiros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.parceiros_id_seq OWNED BY public.parceiros.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id character varying(200) NOT NULL,
    date_created timestamp without time zone
);


--
-- Name: sensors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensors (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    codigo character varying(100) NOT NULL,
    codigo_sonda character varying(100),
    empresa character varying(100),
    tipo_device integer,
    tipo_sonda integer,
    status character varying(50),
    localizacao character varying(100),
    estoque_minimo integer,
    criado_em timestamp without time zone,
    certificado_path character varying(200),
    responsavel_tec character varying(100),
    contato character varying(100),
    data_calibracao date,
    proxima_calibracao date,
    nomenclatura character varying(100),
    local_calibracao character varying(100),
    empresa_calibracao character varying(100)
);


--
-- Name: sensors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sensors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sensors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sensors_id_seq OWNED BY public.sensors.id;


--
-- Name: tipos_device; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipos_device (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    criado_em timestamp without time zone
);


--
-- Name: tipos_device_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipos_device_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_device_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipos_device_id_seq OWNED BY public.tipos_device.id;


--
-- Name: tipos_sonda; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipos_sonda (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    criado_em timestamp without time zone
);


--
-- Name: tipos_sonda_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipos_sonda_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipos_sonda_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipos_sonda_id_seq OWNED BY public.tipos_sonda.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nome character varying(100) NOT NULL,
    email character varying(120) NOT NULL,
    senha_hash character varying(512) NOT NULL,
    reset_token character varying(100),
    permissoes json,
    can_view boolean,
    can_create boolean,
    can_edit boolean,
    can_delete boolean,
    can_export boolean,
    is_admin boolean,
    trocar_senha boolean,
    dashboard_order text
);


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: empresas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresas ALTER COLUMN id SET DEFAULT nextval('public.empresas_id_seq'::regclass);


--
-- Name: estados id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estados ALTER COLUMN id SET DEFAULT nextval('public.estados_id_seq'::regclass);


--
-- Name: municipios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios ALTER COLUMN id SET DEFAULT nextval('public.municipios_id_seq'::regclass);


--
-- Name: parceiros id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parceiros ALTER COLUMN id SET DEFAULT nextval('public.parceiros_id_seq'::regclass);


--
-- Name: sensors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensors ALTER COLUMN id SET DEFAULT nextval('public.sensors_id_seq'::regclass);


--
-- Name: tipos_device id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_device ALTER COLUMN id SET DEFAULT nextval('public.tipos_device_id_seq'::regclass);


--
-- Name: tipos_sonda id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_sonda ALTER COLUMN id SET DEFAULT nextval('public.tipos_sonda_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
f275daf47450
\.


--
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresas (id, nome, cnpj, endereco, telefone, contato, email, cidade, estado, cep, criado_em) FROM stdin;
1	4UIT SOLUCOES EM TI	09.632.190/0001-34	CONCEICAO DE MONTE ALEGRE	(11) 4108-7212	João Silva	CAIO@4UIT.COM.BR	Sao Paulo	SP	04563-060	2025-07-21 16:38:32.392989
2	BIO TRANSPORTES	14.068.428/0001-80	OURINHOS	(11) 2021-0011		RICARDO@BIOTRANSPORTES.COM.BR	Sao Paulo	SP	03186-040	2025-07-21 16:38:32.395892
3	CONCEBER	07.729.132/0001-06	REPUBLICA ARGENTINA	(41) 3039-5556		ALESSANDRO@CLINICACONCEBER.COM.BR	Curitiba	PR	80240-210	2025-07-21 16:38:32.398457
4	CORDVIDA	05.845.263/0001-15	ALVARENGA	(11) 3094-2673		CONTROLADORIA@LABORATORIOCELULASTRONCO.COM.BR	Sao Paulo	SP	05509-006	2025-07-21 16:38:32.400739
5	DBR	08.396.572/0001-43	ALFEU TAVARES (VL AMERICA)	(11) 3907-1433		HELDER@DBRBIOTECH.COM.BR	Sao Bernardo do Campo	SP	09641-000	2025-07-21 16:38:32.403111
6	FERTILITAT - CENTRO DE MEDICINA REPRODUTIVA S/S	94.307.725/0001-70	GOMES JARDIM	(51) 3339-1142		ANAMARIA.GERENCIA@FERTILITAT.COM.BR	Porto Alegre	RS	90620-130	2025-07-21 16:38:32.405059
7	GLOBOAVES SAO PAULO AGROAVICOLA LTDA EM RECUPERACAO JUDICIAL EM RECUPERACAO JUDICIAL	07.580.512/0001-13	JACAREZINHO	(45) 3218-2000		FISCAL@GLOBOAVES.COM.BR	Cascavel	PR	85815-155	2025-07-21 16:38:32.406805
8	GSH CORP PARTICIPACOES S.A	08.397.078/0035-42	SGAS 915 CJ N	(21) 3812-2600		FISCAL@GRUPOGSH.COM	Brasilia	DF	70390-150	2025-07-21 16:38:32.408492
9	HOSPITAL NIPO BRASILEIRO	60.992.427/0006-50	PISTOIA				Sao Paulo	SP	02189-000	2025-07-21 16:38:32.410116
10	HOSPITAL UNIMED LIMEIRA	50.480.953/0002-53	SANTA CRUZ	(19) 3404-4800		DIRETORIA.ADMHOSPITAL@UNIMEDLIMEIRA.COM.BR	Limeira	SP	13480-041	2025-07-21 16:38:32.411782
11	IBRRA - INSTITUTO BRASILEIRO DE REPRODUCAO ASSISTIDA	05.194.929/0001-12	DESEMBARGADOR JORGE FONTANA	(31) 4042-0121		ADM@IBRRA.COM.BR	Belo Horizonte	MG	30320-670	2025-07-21 16:38:32.413369
12	LAB ABS	60.431.863/0001-45	BR 050  KM 196 + 150 METROS	(34) 3336-5177			Delta	MG	38108-000	2025-07-21 16:38:32.414906
13	LAB SAUDE REPRODUTIVA	19.340.529/0001-82	OSCAR FREIRE	(81) 8943-1931		CONTROLADORIA@FERTGROUP.COM.BR	Sao Paulo	SP	05409-011	2025-07-21 16:38:32.419271
14	LA VIE MC LAB	23.334.258/0001-20	SANTO AMARO DE IPITANGA	(71) 9941-6083		GABRIEL@LINOMOTA.COM.BR	Lauro de Freitas	BA	42717-000	2025-07-21 16:38:32.422355
15	MATER LAB	42.102.727/0001-20	IBIRAPUERA	(31) 2552-2009		FINANCEIRO@MATERLAB.COM.BR	Sao Paulo	SP	04029-200	2025-07-21 16:38:32.424954
16	MEDICAR EMERGENCIAS MEDICAS  - CAMPINAS	03.563.718/0001-84	DOUTOR ALBERTO SARMENTO	(19) 3512-1400		FINANCEIRO@MEDICAR.COM.BR	Campinas	SP	13070-711	2025-07-21 16:38:32.427385
17	MEDICAR EMERGENCIAS MEDICAS - RIBEIRÃO	68.322.411/0001-37	CARAMURU	(16) 3512-4477		CONTABILIDADE@MEDICAR.COM.BR	Ribeirao Preto	SP	14030-000	2025-07-21 16:38:32.429815
18	MEDSENIOR ESPIRITO SANTO	31.466.949/0005-39	ALEIXO NETTO	(27) 4007-2001		NF.ES@MEDSENIOR.COM.BR	Vitoria	ES	29055-260	2025-07-21 16:38:32.431678
19	METTA BRASIL LOGISTICA	30.408.555/0001-38	DOUTOR HUGO FORTES	(16) 3917-0890		FINANCEIRO@METTABRASILLOGISTICA.COM.BR	Ribeirao Preto	SP	14095-260	2025-07-21 16:38:32.434133
20	NOVA BIOMEDICAL BRASIL	18.271.934/0001-23	MASSENA	(31) 3360-2510		MCAMPOS@NOVABIOMEDICAL.COM.BR	Nova Lima	MG	34007-746	2025-07-21 16:38:32.436259
21	PROFAM LATAM	34.891.516/0001-95	JOAQUIM FLORIANO	(11) 8208-6354		PERICLES.HASSUN@GMAIL.COM	Sao Paulo	SP	04534-002	2025-07-21 16:38:32.440604
22	PROJETO ALFA - ALIANCA DE LABORATORIOS DE FERTILIZACAO ASSISTIDA S.A.	06.104.430/0001-30	CINCINATO BRAGA	(11) 5645-0835			Sao Paulo	SP	01333-011	2025-07-21 16:38:32.443079
23	PRO-SEED BANCO DE SEMEN	05.377.107/0001-77	PEIXOTO GOMIDE	(11) 3171-1196		FINANCEIRO1@PRO-SEED.COM.BR	Sao Paulo	SP	01409-001	2025-07-21 16:38:32.444696
24	REPRODUCE LABORATORIO	24.892.186/0001-07	VICENTE LAMARCA	(15) 3326-9681		RENEBUSSO@HOTMAIL.COM	Sorocaba	SP	18095-520	2025-07-21 16:38:32.446179
25	SANTA CASA DE PASSOS	23.278.898/0001-60	SANTA CASA	(35) 3529-1371		CONTABILIDADE@SCPASSOS.ORG.BR	Passos	MG	37904-020	2025-07-21 16:38:32.447933
26	VIDA FERTIL-BANCO DE SEMEN LTDA	23.170.302/0001-03	OSVALDO ARANHA	(51) 9578-8525		CONTATO@CENTROVIDAFERTIL.COM.BR	Porto Alegre	RS	90035-191	2025-07-21 16:38:32.449682
\.


--
-- Data for Name: estados; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estados (id, sigla, nome) FROM stdin;
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locations (location_id, date_created) FROM stdin;
\.


--
-- Data for Name: municipios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.municipios (id, nome, estado_id) FROM stdin;
\.


--
-- Data for Name: parceiros; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parceiros (id, nome, telefone, cidade, uf, cpf, pix, cep, rua, numero, complemento, bairro) FROM stdin;
1	Fabio Nobre	1141087212	\N		309.455.538-11	21321321	07713040	Rua Sorocaba	271		Serpa
\.


--
-- Data for Name: parceiros_empresas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parceiros_empresas (parceiro_id, empresa_id) FROM stdin;
1	1
1	3
1	2
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (product_id, date_created) FROM stdin;
\.


--
-- Data for Name: sensors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sensors (id, nome, codigo, codigo_sonda, empresa, tipo_device, tipo_sonda, status, localizacao, estoque_minimo, criado_em, certificado_path, responsavel_tec, contato, data_calibracao, proxima_calibracao, nomenclatura, local_calibracao, empresa_calibracao) FROM stdin;
1	WE	216454939431738	5156165	GLOBOAVES SAO PAULO AGROAVICOLA LTDA EM RECUPERACAO JUDICIAL EM RECUPERACAO JUDICIAL	1	2	Em estoque	Laboratorio	\N	2025-07-21 19:19:03.812224	\N	UERLEI	021 34 991986325	2024-12-06	2025-12-06	VACINAS VIVAS	in loco	MSMI
2	Nodo PT100	DACASDCREWRWE	WERQW23	MATER LAB	3	8	Em uso	Laboratorio	\N	2025-07-21 19:20:00.431803	\N	Fabio	324233211234	2025-02-06	2025-08-02	TANK	Laboratorio	MSMI
3	Nodo CO2 + TH	R32324	E32E332	SANTA CASA DE PASSOS	5	9	Em uso	Laboratorio	\N	2025-07-21 19:20:36.650127	certificados/Certificado_de_Calibracao_-_Sensor_1554541.pdf	Fabio	32D32	2025-06-05	2025-08-27	GELADEIRA 1	in loco	MSMI
\.


--
-- Data for Name: tipos_device; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipos_device (id, nome, criado_em) FROM stdin;
1	WE	2025-07-21 16:40:38.865846
2	MB	2025-07-21 16:40:41.915389
3	Nodo PT100	2025-07-21 16:40:44.948159
4	Nodo TH	2025-07-21 16:40:47.965182
5	Nodo CO2 + TH	2025-07-21 16:40:51.302623
\.


--
-- Data for Name: tipos_sonda; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipos_sonda (id, nome, criado_em) FROM stdin;
1	Sonda pitoco TH	2025-07-21 16:39:58.880405
3	DS18B20 temperatura cabo normal	2025-07-21 16:40:05.353053
4	SHT31 temperatura e umidade cabo fino	2025-07-21 16:40:08.213039
5	SHT31 temperatura e umidade cabo normal	2025-07-21 16:40:11.978784
6	Sonda CO2 e TH	2025-07-21 16:40:15.403022
7	Sonda interna (nodo)	2025-07-21 16:40:18.363665
8	PT100 nodo	2025-07-21 16:40:24.7014
9	PT100 com placa para WE e MB	2025-07-21 16:40:31.98313
2	M12- DS18B20 Temperatura cabo fino	2025-07-21 16:40:02.531559
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id, nome, email, senha_hash, reset_token, permissoes, can_view, can_create, can_edit, can_delete, can_export, is_admin, trocar_senha, dashboard_order) FROM stdin;
1	Admin	admin@admin.com	scrypt:32768:8:1$L4qvwY6saMIaELA6$852c516e70ccadebbb98a7b2ab4bc29455424a7c8588ab7b9b9fa90edcc357c8229a6a3771e882253dd51aba81a39a53dd20f03cbdde5510e1460dbdaebb97d5	\N	"admin"	t	t	t	t	t	t	f	[{"id": "chartDevice", "title": "Sensores por Tipo de Device (%)", "w": 4, "h": 2, "x": 0, "y": 0}, {"id": "chartTipoSonda", "title": "Sensores por Tipo de Sonda", "w": 4, "h": 2, "x": 4, "y": 0}, {"id": "chartUF", "title": "Sensores por Estado (UF)", "w": 4, "h": 2, "x": 8, "y": 0}, {"id": "chartStatus", "title": "Sensores por Status", "w": 4, "h": 3, "x": 0, "y": 2}]
\.


--
-- Name: empresas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresas_id_seq', 26, true);


--
-- Name: estados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estados_id_seq', 1, false);


--
-- Name: municipios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.municipios_id_seq', 1, false);


--
-- Name: parceiros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.parceiros_id_seq', 1, true);


--
-- Name: sensors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sensors_id_seq', 4, true);


--
-- Name: tipos_device_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipos_device_id_seq', 5, true);


--
-- Name: tipos_sonda_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipos_sonda_id_seq', 9, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: empresas empresas_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_nome_key UNIQUE (nome);


--
-- Name: empresas empresas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_pkey PRIMARY KEY (id);


--
-- Name: estados estados_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estados
    ADD CONSTRAINT estados_pkey PRIMARY KEY (id);


--
-- Name: estados estados_sigla_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estados
    ADD CONSTRAINT estados_sigla_key UNIQUE (sigla);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (location_id);


--
-- Name: municipios municipios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_pkey PRIMARY KEY (id);


--
-- Name: parceiros parceiros_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parceiros
    ADD CONSTRAINT parceiros_nome_key UNIQUE (nome);


--
-- Name: parceiros parceiros_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parceiros
    ADD CONSTRAINT parceiros_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: sensors sensors_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_codigo_key UNIQUE (codigo);


--
-- Name: sensors sensors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_pkey PRIMARY KEY (id);


--
-- Name: tipos_device tipos_device_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_device
    ADD CONSTRAINT tipos_device_nome_key UNIQUE (nome);


--
-- Name: tipos_device tipos_device_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_device
    ADD CONSTRAINT tipos_device_pkey PRIMARY KEY (id);


--
-- Name: tipos_sonda tipos_sonda_nome_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_sonda
    ADD CONSTRAINT tipos_sonda_nome_key UNIQUE (nome);


--
-- Name: tipos_sonda tipos_sonda_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipos_sonda
    ADD CONSTRAINT tipos_sonda_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: municipios municipios_estado_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.municipios
    ADD CONSTRAINT municipios_estado_id_fkey FOREIGN KEY (estado_id) REFERENCES public.estados(id);


--
-- Name: parceiros_empresas parceiros_empresas_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parceiros_empresas
    ADD CONSTRAINT parceiros_empresas_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: parceiros_empresas parceiros_empresas_parceiro_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parceiros_empresas
    ADD CONSTRAINT parceiros_empresas_parceiro_id_fkey FOREIGN KEY (parceiro_id) REFERENCES public.parceiros(id);


--
-- Name: sensors sensors_tipo_device_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_tipo_device_fkey FOREIGN KEY (tipo_device) REFERENCES public.tipos_device(id);


--
-- Name: sensors sensors_tipo_sonda_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sensors
    ADD CONSTRAINT sensors_tipo_sonda_fkey FOREIGN KEY (tipo_sonda) REFERENCES public.tipos_sonda(id);


--
-- PostgreSQL database dump complete
--

