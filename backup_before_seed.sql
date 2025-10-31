--
-- PostgreSQL database dump
--

\restrict coKA7hDEyXejbtTudLl8G3nFjUi6U9EWRVnuEqGxP5wWQIxuRt0Ttmn4IYSxLgq

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

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
-- Name: activity_log; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.activity_log (
    id integer NOT NULL,
    user_id integer,
    action character varying,
    resource_type character varying,
    resource_id integer,
    details jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp without time zone
);


ALTER TABLE public.activity_log OWNER TO reelbrief_user;

--
-- Name: activity_log_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.activity_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_log_id_seq OWNER TO reelbrief_user;

--
-- Name: activity_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.activity_log_id_seq OWNED BY public.activity_log.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO reelbrief_user;

--
-- Name: deliverables; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.deliverables (
    id integer NOT NULL,
    project_id integer NOT NULL,
    uploaded_by integer NOT NULL,
    reviewed_by integer,
    version_number integer NOT NULL,
    file_url text NOT NULL,
    file_type character varying(50),
    file_size integer,
    cloudinary_public_id character varying(255),
    thumbnail_url text,
    title character varying(255),
    description text,
    change_notes text,
    status character varying(20) NOT NULL,
    uploaded_at timestamp without time zone NOT NULL,
    reviewed_at timestamp without time zone
);


ALTER TABLE public.deliverables OWNER TO reelbrief_user;

--
-- Name: deliverables_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.deliverables_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.deliverables_id_seq OWNER TO reelbrief_user;

--
-- Name: deliverables_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.deliverables_id_seq OWNED BY public.deliverables.id;


--
-- Name: escrow_transactions; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.escrow_transactions (
    id integer NOT NULL,
    project_id integer NOT NULL,
    client_id integer NOT NULL,
    freelancer_id integer NOT NULL,
    admin_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character varying(10) NOT NULL,
    status character varying(20) NOT NULL,
    invoice_number character varying(50) NOT NULL,
    invoice_url character varying(255),
    payment_method character varying(50),
    held_at timestamp without time zone,
    released_at timestamp without time zone,
    refunded_at timestamp without time zone,
    notes text
);


ALTER TABLE public.escrow_transactions OWNER TO reelbrief_user;

--
-- Name: escrow_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.escrow_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.escrow_transactions_id_seq OWNER TO reelbrief_user;

--
-- Name: escrow_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.escrow_transactions_id_seq OWNED BY public.escrow_transactions.id;


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    deliverable_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_feedback_id integer,
    feedback_type character varying(20) NOT NULL,
    content text NOT NULL,
    priority character varying(20),
    is_resolved boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    resolved_at timestamp without time zone
);


ALTER TABLE public.feedback OWNER TO reelbrief_user;

--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_id_seq OWNER TO reelbrief_user;

--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- Name: freelancer; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.freelancer (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    bio text,
    cv_url character varying(300),
    portfolio_url character varying(300),
    years_experience integer,
    hourly_rate double precision,
    application_status character varying(20),
    rejection_reason text,
    created_at timestamp without time zone
);


ALTER TABLE public.freelancer OWNER TO reelbrief_user;

--
-- Name: freelancer_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.freelancer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.freelancer_id_seq OWNER TO reelbrief_user;

--
-- Name: freelancer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.freelancer_id_seq OWNED BY public.freelancer.id;


--
-- Name: freelancer_profiles; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.freelancer_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    bio text,
    portfolio_url character varying(255),
    years_experience integer,
    hourly_rate double precision,
    cv_url character varying(255),
    cv_filename character varying(255),
    cv_uploaded_at timestamp without time zone,
    application_status character varying(20),
    rejection_reason character varying(255),
    approved_at timestamp without time zone,
    approved_by integer,
    open_to_work boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.freelancer_profiles OWNER TO reelbrief_user;

--
-- Name: freelancer_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.freelancer_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.freelancer_profiles_id_seq OWNER TO reelbrief_user;

--
-- Name: freelancer_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.freelancer_profiles_id_seq OWNED BY public.freelancer_profiles.id;


--
-- Name: freelancer_skills; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.freelancer_skills (
    id integer NOT NULL,
    freelancer_id integer NOT NULL,
    skill_id integer NOT NULL,
    proficiency character varying(50)
);


ALTER TABLE public.freelancer_skills OWNER TO reelbrief_user;

--
-- Name: freelancer_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.freelancer_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.freelancer_skills_id_seq OWNER TO reelbrief_user;

--
-- Name: freelancer_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.freelancer_skills_id_seq OWNED BY public.freelancer_skills.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    project_id integer NOT NULL,
    client_id integer NOT NULL,
    freelancer_id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    amount numeric(10,2) NOT NULL,
    currency character varying(10) NOT NULL,
    issue_date timestamp without time zone,
    due_date timestamp without time zone,
    paid_at timestamp without time zone,
    status character varying(20) NOT NULL,
    pdf_url character varying(255),
    notes text,
    escrow_id integer
);


ALTER TABLE public.invoices OWNER TO reelbrief_user;

--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoices_id_seq OWNER TO reelbrief_user;

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    related_project_id integer,
    related_deliverable_id integer,
    is_read boolean,
    is_emailed boolean,
    email_sent_at timestamp without time zone,
    created_at timestamp without time zone
);


ALTER TABLE public.notifications OWNER TO reelbrief_user;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO reelbrief_user;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: portfolio_items; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.portfolio_items (
    id integer NOT NULL,
    freelancer_id integer NOT NULL,
    project_id integer NOT NULL,
    title character varying(150) NOT NULL,
    description text,
    cover_image_url character varying(255),
    project_url character varying(255),
    tags character varying[],
    display_order integer,
    is_featured boolean,
    is_visible boolean,
    created_at timestamp without time zone
);


ALTER TABLE public.portfolio_items OWNER TO reelbrief_user;

--
-- Name: portfolio_items_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.portfolio_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.portfolio_items_id_seq OWNER TO reelbrief_user;

--
-- Name: portfolio_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.portfolio_items_id_seq OWNED BY public.portfolio_items.id;


--
-- Name: project_skills; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.project_skills (
    id integer NOT NULL,
    project_id integer NOT NULL,
    skill_id integer NOT NULL,
    required_proficiency character varying(50)
);


ALTER TABLE public.project_skills OWNER TO reelbrief_user;

--
-- Name: project_skills_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.project_skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.project_skills_id_seq OWNER TO reelbrief_user;

--
-- Name: project_skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.project_skills_id_seq OWNED BY public.project_skills.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    title character varying(150) NOT NULL,
    description text NOT NULL,
    client_id integer NOT NULL,
    freelancer_id integer,
    admin_id integer,
    status character varying(50),
    budget numeric(10,2),
    deadline timestamp without time zone,
    is_sensitive boolean,
    payment_status character varying(50),
    project_type character varying(100),
    priority character varying(50),
    created_at timestamp without time zone,
    matched_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    cancelled_at timestamp without time zone,
    cancellation_reason text
);


ALTER TABLE public.projects OWNER TO reelbrief_user;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projects_id_seq OWNER TO reelbrief_user;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.reviews (
    id integer NOT NULL,
    project_id integer NOT NULL,
    client_id integer NOT NULL,
    freelancer_id integer NOT NULL,
    rating integer NOT NULL,
    communication_rating integer,
    quality_rating integer,
    timeliness_rating integer,
    review_text text,
    is_public boolean,
    created_at timestamp without time zone,
    CONSTRAINT reviews_communication_rating_check CHECK (((communication_rating >= 1) AND (communication_rating <= 5))),
    CONSTRAINT reviews_quality_rating_check CHECK (((quality_rating >= 1) AND (quality_rating <= 5))),
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5))),
    CONSTRAINT reviews_timeliness_rating_check CHECK (((timeliness_rating >= 1) AND (timeliness_rating <= 5)))
);


ALTER TABLE public.reviews OWNER TO reelbrief_user;

--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.reviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reviews_id_seq OWNER TO reelbrief_user;

--
-- Name: reviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.reviews_id_seq OWNED BY public.reviews.id;


--
-- Name: skills; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.skills (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    category character varying(100),
    created_at timestamp without time zone
);


ALTER TABLE public.skills OWNER TO reelbrief_user;

--
-- Name: skills_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.skills_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skills_id_seq OWNER TO reelbrief_user;

--
-- Name: skills_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.skills_id_seq OWNED BY public.skills.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    phone character varying(50),
    avatar_url character varying(255),
    bio text,
    role character varying(50) NOT NULL,
    is_active boolean,
    is_verified boolean,
    verification_token character varying(255),
    reset_token character varying(255),
    reset_token_expires timestamp without time zone,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO reelbrief_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO reelbrief_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: activity_log id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_log ALTER COLUMN id SET DEFAULT nextval('public.activity_log_id_seq'::regclass);


--
-- Name: deliverables id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.deliverables ALTER COLUMN id SET DEFAULT nextval('public.deliverables_id_seq'::regclass);


--
-- Name: escrow_transactions id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions ALTER COLUMN id SET DEFAULT nextval('public.escrow_transactions_id_seq'::regclass);


--
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- Name: freelancer id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer ALTER COLUMN id SET DEFAULT nextval('public.freelancer_id_seq'::regclass);


--
-- Name: freelancer_profiles id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles ALTER COLUMN id SET DEFAULT nextval('public.freelancer_profiles_id_seq'::regclass);


--
-- Name: freelancer_skills id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_skills ALTER COLUMN id SET DEFAULT nextval('public.freelancer_skills_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: portfolio_items id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.portfolio_items ALTER COLUMN id SET DEFAULT nextval('public.portfolio_items_id_seq'::regclass);


--
-- Name: project_skills id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.project_skills ALTER COLUMN id SET DEFAULT nextval('public.project_skills_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: reviews id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews ALTER COLUMN id SET DEFAULT nextval('public.reviews_id_seq'::regclass);


--
-- Name: skills id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.skills ALTER COLUMN id SET DEFAULT nextval('public.skills_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: activity_log; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.activity_log (id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.alembic_version (version_num) FROM stdin;
7f8c4b03abd6
\.


--
-- Data for Name: deliverables; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.deliverables (id, project_id, uploaded_by, reviewed_by, version_number, file_url, file_type, file_size, cloudinary_public_id, thumbnail_url, title, description, change_notes, status, uploaded_at, reviewed_at) FROM stdin;
\.


--
-- Data for Name: escrow_transactions; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.escrow_transactions (id, project_id, client_id, freelancer_id, admin_id, amount, currency, status, invoice_number, invoice_url, payment_method, held_at, released_at, refunded_at, notes) FROM stdin;
\.


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.feedback (id, deliverable_id, user_id, parent_feedback_id, feedback_type, content, priority, is_resolved, created_at, resolved_at) FROM stdin;
\.


--
-- Data for Name: freelancer; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.freelancer (id, name, email, bio, cv_url, portfolio_url, years_experience, hourly_rate, application_status, rejection_reason, created_at) FROM stdin;
\.


--
-- Data for Name: freelancer_profiles; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.freelancer_profiles (id, user_id, name, email, bio, portfolio_url, years_experience, hourly_rate, cv_url, cv_filename, cv_uploaded_at, application_status, rejection_reason, approved_at, approved_by, open_to_work, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: freelancer_skills; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.freelancer_skills (id, freelancer_id, skill_id, proficiency) FROM stdin;
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.invoices (id, project_id, client_id, freelancer_id, invoice_number, amount, currency, issue_date, due_date, paid_at, status, pdf_url, notes, escrow_id) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.notifications (id, user_id, type, title, message, related_project_id, related_deliverable_id, is_read, is_emailed, email_sent_at, created_at) FROM stdin;
\.


--
-- Data for Name: portfolio_items; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.portfolio_items (id, freelancer_id, project_id, title, description, cover_image_url, project_url, tags, display_order, is_featured, is_visible, created_at) FROM stdin;
\.


--
-- Data for Name: project_skills; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.project_skills (id, project_id, skill_id, required_proficiency) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.projects (id, title, description, client_id, freelancer_id, admin_id, status, budget, deadline, is_sensitive, payment_status, project_type, priority, created_at, matched_at, started_at, completed_at, cancelled_at, cancellation_reason) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.reviews (id, project_id, client_id, freelancer_id, rating, communication_rating, quality_rating, timeliness_rating, review_text, is_public, created_at) FROM stdin;
\.


--
-- Data for Name: skills; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.skills (id, name, category, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.users (id, email, password_hash, first_name, last_name, phone, avatar_url, bio, role, is_active, is_verified, verification_token, reset_token, reset_token_expires, created_at, updated_at, last_login) FROM stdin;
8	admin@reelbrief.com	scrypt:32768:8:1$ZT08oChwPgPhVCee$c6cfec0646c29c06e694c64cbf3179e5fbcfb0feb0a2c8c144351f9de1f983605176ca6484059efd9c3827e082b2c2010dc1293748b9228811c5d9fffac04f7f	Admin	User	\N	\N	\N	admin	t	f	\N	\N	\N	2025-10-30 07:10:59.331266	2025-10-30 07:11:30.159519	2025-10-30 07:11:30.045749
9	freelancer@reelbrief.com	scrypt:32768:8:1$peDKioF5emGQeQ6J$c6be9db2a558da1f3cf8468c6425aa1f179098bcf005570eea66e3722c5690332d81a5cba34a66614a622554cb7a69ef9744aeb7a0eb105bf3331265eebefed7	Freelancer	One	\N	\N	\N	freelancer	t	f	\N	\N	\N	2025-10-30 07:10:59.331298	2025-10-30 07:11:31.067112	2025-10-30 07:11:31.063539
10	client@reelbrief.com	scrypt:32768:8:1$sB1ftlQIJjzRBtxR$ecfa07bcfea590cd92e1b1d5274568d75885adac5423a0981a996c00ea834d40f6ba9b78f4b0bf5b9d9b7c420ab2a4b7f5fe3f2dce2c35e0d10afb2535c3afc8	Client	One	\N	\N	\N	client	t	f	\N	\N	\N	2025-10-30 07:10:59.331309	2025-10-30 07:11:32.056517	2025-10-30 07:11:32.053175
\.


--
-- Name: activity_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.activity_log_id_seq', 1, false);


--
-- Name: deliverables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.deliverables_id_seq', 1, false);


--
-- Name: escrow_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.escrow_transactions_id_seq', 1, false);


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.feedback_id_seq', 1, false);


--
-- Name: freelancer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.freelancer_id_seq', 1, false);


--
-- Name: freelancer_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.freelancer_profiles_id_seq', 1, false);


--
-- Name: freelancer_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.freelancer_skills_id_seq', 1, false);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.invoices_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: portfolio_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.portfolio_items_id_seq', 1, false);


--
-- Name: project_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.project_skills_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.projects_id_seq', 1, false);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.reviews_id_seq', 1, false);


--
-- Name: skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.skills_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.users_id_seq', 10, true);


--
-- Name: activity_log activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: deliverables deliverables_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_pkey PRIMARY KEY (id);


--
-- Name: escrow_transactions escrow_transactions_invoice_number_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_invoice_number_key UNIQUE (invoice_number);


--
-- Name: escrow_transactions escrow_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_pkey PRIMARY KEY (id);


--
-- Name: escrow_transactions escrow_transactions_project_id_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_project_id_key UNIQUE (project_id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: freelancer freelancer_email_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer
    ADD CONSTRAINT freelancer_email_key UNIQUE (email);


--
-- Name: freelancer freelancer_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer
    ADD CONSTRAINT freelancer_pkey PRIMARY KEY (id);


--
-- Name: freelancer_profiles freelancer_profiles_email_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles
    ADD CONSTRAINT freelancer_profiles_email_key UNIQUE (email);


--
-- Name: freelancer_profiles freelancer_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles
    ADD CONSTRAINT freelancer_profiles_pkey PRIMARY KEY (id);


--
-- Name: freelancer_profiles freelancer_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles
    ADD CONSTRAINT freelancer_profiles_user_id_key UNIQUE (user_id);


--
-- Name: freelancer_skills freelancer_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_skills
    ADD CONSTRAINT freelancer_skills_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_invoice_number_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_invoice_number_key UNIQUE (invoice_number);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: portfolio_items portfolio_items_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.portfolio_items
    ADD CONSTRAINT portfolio_items_pkey PRIMARY KEY (id);


--
-- Name: portfolio_items portfolio_items_project_id_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.portfolio_items
    ADD CONSTRAINT portfolio_items_project_id_key UNIQUE (project_id);


--
-- Name: project_skills project_skills_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.project_skills
    ADD CONSTRAINT project_skills_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_project_id_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_project_id_key UNIQUE (project_id);


--
-- Name: skills skills_name_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_name_key UNIQUE (name);


--
-- Name: skills skills_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.skills
    ADD CONSTRAINT skills_pkey PRIMARY KEY (id);


--
-- Name: project_skills uq_project_skill; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.project_skills
    ADD CONSTRAINT uq_project_skill UNIQUE (project_id, skill_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_verification_token_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_verification_token_key UNIQUE (verification_token);


--
-- Name: idx_deliverables_project; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_deliverables_project ON public.deliverables USING btree (project_id);


--
-- Name: idx_deliverables_version; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_deliverables_version ON public.deliverables USING btree (project_id, version_number);


--
-- Name: idx_feedback_deliverable; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_feedback_deliverable ON public.feedback USING btree (deliverable_id);


--
-- Name: idx_feedback_user; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_feedback_user ON public.feedback USING btree (user_id);


--
-- Name: idx_resource; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_resource ON public.activity_log USING btree (resource_type, resource_id);


--
-- Name: idx_user_id; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_user_id ON public.activity_log USING btree (user_id);


--
-- Name: idx_user_unread; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_user_unread ON public.notifications USING btree (user_id, is_read);


--
-- Name: activity_log activity_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: deliverables deliverables_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: deliverables deliverables_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- Name: deliverables deliverables_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.deliverables
    ADD CONSTRAINT deliverables_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: escrow_transactions escrow_transactions_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: escrow_transactions escrow_transactions_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: escrow_transactions escrow_transactions_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.users(id);


--
-- Name: escrow_transactions escrow_transactions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.escrow_transactions
    ADD CONSTRAINT escrow_transactions_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: feedback feedback_deliverable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_deliverable_id_fkey FOREIGN KEY (deliverable_id) REFERENCES public.deliverables(id) ON DELETE CASCADE;


--
-- Name: feedback feedback_parent_feedback_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_parent_feedback_id_fkey FOREIGN KEY (parent_feedback_id) REFERENCES public.feedback(id);


--
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: freelancer_profiles freelancer_profiles_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles
    ADD CONSTRAINT freelancer_profiles_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: freelancer_profiles freelancer_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_profiles
    ADD CONSTRAINT freelancer_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: freelancer_skills freelancer_skills_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_skills
    ADD CONSTRAINT freelancer_skills_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.freelancer_profiles(id);


--
-- Name: freelancer_skills freelancer_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.freelancer_skills
    ADD CONSTRAINT freelancer_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id);


--
-- Name: invoices invoices_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: invoices invoices_escrow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_escrow_id_fkey FOREIGN KEY (escrow_id) REFERENCES public.escrow_transactions(id);


--
-- Name: invoices invoices_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.users(id);


--
-- Name: invoices invoices_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: notifications notifications_related_deliverable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_deliverable_id_fkey FOREIGN KEY (related_deliverable_id) REFERENCES public.deliverables(id);


--
-- Name: notifications notifications_related_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_project_id_fkey FOREIGN KEY (related_project_id) REFERENCES public.projects(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: portfolio_items portfolio_items_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.portfolio_items
    ADD CONSTRAINT portfolio_items_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.users(id);


--
-- Name: portfolio_items portfolio_items_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.portfolio_items
    ADD CONSTRAINT portfolio_items_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: project_skills project_skills_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.project_skills
    ADD CONSTRAINT project_skills_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: project_skills project_skills_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.project_skills
    ADD CONSTRAINT project_skills_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skills(id);


--
-- Name: projects projects_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.users(id);


--
-- Name: projects projects_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: projects projects_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.users(id);


--
-- Name: reviews reviews_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.users(id);


--
-- Name: reviews reviews_freelancer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_freelancer_id_fkey FOREIGN KEY (freelancer_id) REFERENCES public.users(id);


--
-- Name: reviews reviews_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO reelbrief_user;


--
-- PostgreSQL database dump complete
--

\unrestrict coKA7hDEyXejbtTudLl8G3nFjUi6U9EWRVnuEqGxP5wWQIxuRt0Ttmn4IYSxLgq

