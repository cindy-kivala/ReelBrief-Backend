--
-- PostgreSQL database dump
--

\restrict eeTlPo4J84Xb2Ya64H8DbGiMQOjKuCFCT2BIrFx4g4B8ohAzapWU7uNHPnT61bT

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg12+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-2.pgdg13+1)

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

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: reelbrief_user
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO reelbrief_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_logs; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.activity_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(100) NOT NULL,
    resource_type character varying(50) NOT NULL,
    resource_id integer,
    details json,
    created_at timestamp without time zone
);


ALTER TABLE public.activity_logs OWNER TO reelbrief_user;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.activity_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.activity_logs_id_seq OWNER TO reelbrief_user;

--
-- Name: activity_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.activity_logs_id_seq OWNED BY public.activity_logs.id;


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
    cancellation_reason text,
    approved_at timestamp without time zone,
    approved_by integer,
    rejection_reason text,
    assignment_requested boolean DEFAULT false,
    assigned_at timestamp without time zone
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
-- Name: wallet_transactions; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.wallet_transactions (
    id integer NOT NULL,
    wallet_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    transaction_type character varying(20) NOT NULL,
    description character varying(255),
    reference_id integer,
    created_at timestamp without time zone
);


ALTER TABLE public.wallet_transactions OWNER TO reelbrief_user;

--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.wallet_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wallet_transactions_id_seq OWNER TO reelbrief_user;

--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.wallet_transactions_id_seq OWNED BY public.wallet_transactions.id;


--
-- Name: wallets; Type: TABLE; Schema: public; Owner: reelbrief_user
--

CREATE TABLE public.wallets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    balance numeric(10,2),
    currency character varying(10) NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.wallets OWNER TO reelbrief_user;

--
-- Name: wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: reelbrief_user
--

CREATE SEQUENCE public.wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wallets_id_seq OWNER TO reelbrief_user;

--
-- Name: wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: reelbrief_user
--

ALTER SEQUENCE public.wallets_id_seq OWNED BY public.wallets.id;


--
-- Name: activity_logs id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_logs ALTER COLUMN id SET DEFAULT nextval('public.activity_logs_id_seq'::regclass);


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
-- Name: wallet_transactions id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallet_transactions ALTER COLUMN id SET DEFAULT nextval('public.wallet_transactions_id_seq'::regclass);


--
-- Name: wallets id; Type: DEFAULT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallets ALTER COLUMN id SET DEFAULT nextval('public.wallets_id_seq'::regclass);


--
-- Data for Name: activity_logs; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.activity_logs (id, user_id, action, resource_type, resource_id, details, created_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.alembic_version (version_num) FROM stdin;
9b449846d4a2
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
13	27	Alex Thompson	alex@designer.com	UI/UX designer with 5+ years experience creating beautiful and functional digital products.	https://alexthompson.design	5	85	\N	\N	\N	approved	\N	2025-11-03 19:33:36.363276	20	t	2025-11-03 19:33:36.717397	2025-11-03 19:33:36.717407
14	28	Priya Patel	priya@developer.com	Full-stack developer specializing in React, Node.js, and Python with video editing skills.	https://priyapatel.dev	7	95	\N	\N	\N	approved	\N	2025-11-03 19:33:38.73648	20	t	2025-11-03 19:33:39.250399	2025-11-03 19:33:39.25041
15	29	Carlos Martinez	carlos@animator.com	3D animator and motion graphics artist with expertise in Blender and Cinema 4D.	https://carlosanimation.com	8	110	\N	\N	\N	approved	\N	2025-11-03 19:33:41.239008	20	t	2025-11-03 19:33:41.708265	2025-11-03 19:33:41.708276
16	30	Lisa Zhang	lisa@writer.com	Content writer and copywriter specializing in tech and marketing content.	https://lisazhangwriting.com	4	65	\N	\N	\N	approved	\N	2025-11-03 19:33:43.648439	20	f	2025-11-03 19:33:44.181229	2025-11-03 19:33:44.181245
17	31	Sophia Garcia	sophia@marketing.com	Digital marketing expert with focus on social media and analytics.	https://sophiamarketing.com	6	75	\N	\N	\N	pending	\N	\N	\N	t	2025-11-03 19:33:45.802364	2025-11-03 19:33:45.802377
18	32	Marcus Johnson	marcus@mobile.dev	Mobile app developer specializing in React Native and Flutter cross-platform solutions.	https://marcusmobile.dev	5	90	\N	\N	\N	approved	\N	2025-11-03 19:33:47.848322	20	t	2025-11-03 19:33:48.169977	2025-11-03 19:33:48.169988
19	33	Natalie Chen	natalie@graphics.com	Graphic designer and illustrator with a passion for branding and visual identity.	https://nataliechen.design	4	70	\N	\N	\N	approved	\N	2025-11-03 19:33:50.100655	20	t	2025-11-03 19:33:50.920842	2025-11-03 19:33:50.920852
20	34	Ryan O'Connor	ryan@videopro.com	Professional video editor and filmmaker with expertise in Premiere Pro and After Effects.	https://ryanoconnorfilms.com	6	85	\N	\N	\N	approved	\N	2025-11-03 19:33:53.482835	20	t	2025-11-03 19:33:53.993871	2025-11-03 19:33:53.993882
21	35	Taylor Brown	taylor@fullstack.io	Full-stack developer with expertise in modern web technologies and cloud infrastructure.	https://taylorbrown.dev	7	100	\N	\N	\N	approved	\N	2025-11-03 19:33:55.936394	20	t	2025-11-03 19:33:56.351336	2025-11-03 19:33:56.35135
22	36	Isabella Rossi	isabella@content.co	Content strategist and SEO specialist helping brands improve their online presence.	https://isabellarossi.com	5	60	\N	\N	\N	approved	\N	2025-11-03 19:33:58.615721	20	t	2025-11-03 19:33:58.924212	2025-11-03 19:33:58.924225
23	37	Kevin Nguyen	kevin@devops.tech	DevOps engineer specializing in cloud infrastructure, CI/CD, and system architecture.	https://kevinnguyen.tech	8	120	\N	\N	\N	approved	\N	2025-11-03 19:34:01.265894	20	f	2025-11-03 19:34:01.587872	2025-11-03 19:34:01.587883
24	38	Olivia Park	olivia@uiux.design	UI/UX designer focused on creating intuitive and accessible digital experiences.	https://oliviapark.design	4	80	\N	\N	\N	approved	\N	2025-11-03 19:34:03.513674	20	t	2025-11-03 19:34:03.836699	2025-11-03 19:34:03.83671
\.


--
-- Data for Name: freelancer_skills; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.freelancer_skills (id, freelancer_id, skill_id, proficiency) FROM stdin;
57	13	57	intermediate
58	13	58	beginner
59	13	61	beginner
60	13	62	intermediate
61	14	63	intermediate
62	14	64	expert
63	14	65	beginner
64	14	66	intermediate
65	14	68	expert
66	14	96	expert
67	15	69	beginner
68	15	70	intermediate
69	15	71	beginner
70	15	72	expert
71	15	67	beginner
72	16	73	intermediate
73	16	74	beginner
74	16	75	beginner
75	16	76	expert
76	16	77	beginner
77	17	78	beginner
78	17	74	intermediate
79	17	79	intermediate
80	17	80	beginner
81	18	88	intermediate
82	18	87	expert
83	18	82	beginner
84	18	68	beginner
85	19	83	expert
86	19	84	beginner
87	19	103	expert
88	19	104	intermediate
89	20	66	intermediate
90	20	71	intermediate
91	20	106	beginner
92	20	67	intermediate
93	21	63	expert
94	21	64	intermediate
95	21	65	beginner
96	21	97	expert
97	21	98	expert
98	21	95	expert
99	22	73	expert
100	22	74	expert
101	22	112	beginner
102	22	108	intermediate
103	23	97	intermediate
104	23	98	expert
105	23	99	beginner
106	23	100	beginner
107	23	65	beginner
108	24	57	expert
109	24	58	beginner
110	24	60	beginner
111	24	62	beginner
112	24	61	beginner
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

COPY public.projects (id, title, description, client_id, freelancer_id, admin_id, status, budget, deadline, is_sensitive, payment_status, project_type, priority, created_at, matched_at, started_at, completed_at, cancelled_at, cancellation_reason, approved_at, approved_by, rejection_reason, assignment_requested, assigned_at) FROM stdin;
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
57	UI/UX Design	\N	2025-11-03 19:33:24.114651
58	Figma	\N	2025-11-03 19:33:24.114664
59	Sketch	\N	2025-11-03 19:33:24.114668
60	Adobe XD	\N	2025-11-03 19:33:24.114672
61	Prototyping	\N	2025-11-03 19:33:24.114688
62	User Research	\N	2025-11-03 19:33:24.114693
63	React	\N	2025-11-03 19:33:24.114695
64	Node.js	\N	2025-11-03 19:33:24.114699
65	Python	\N	2025-11-03 19:33:24.114702
66	Video Editing	\N	2025-11-03 19:33:24.114705
67	Motion Graphics	\N	2025-11-03 19:33:24.114707
68	JavaScript	\N	2025-11-03 19:33:24.114709
69	Blender	\N	2025-11-03 19:33:24.114711
70	Cinema 4D	\N	2025-11-03 19:33:24.114714
71	After Effects	\N	2025-11-03 19:33:24.114716
72	3D Animation	\N	2025-11-03 19:33:24.114718
73	Content Writing	\N	2025-11-03 19:33:24.114721
74	SEO	\N	2025-11-03 19:33:24.114723
75	Marketing Copy	\N	2025-11-03 19:33:24.114725
76	Technical Writing	\N	2025-11-03 19:33:24.114727
77	Copywriting	\N	2025-11-03 19:33:24.114729
78	Social Media Marketing	\N	2025-11-03 19:33:24.114731
79	Analytics	\N	2025-11-03 19:33:24.114733
80	Campaign Management	\N	2025-11-03 19:33:24.114736
81	Web Development	\N	2025-11-03 19:33:24.114738
82	Mobile Development	\N	2025-11-03 19:33:24.11474
83	Graphic Design	\N	2025-11-03 19:33:24.114742
84	Illustration	\N	2025-11-03 19:33:24.114744
85	Swift	\N	2025-11-03 19:33:24.114746
86	Kotlin	\N	2025-11-03 19:33:24.114748
87	Flutter	\N	2025-11-03 19:33:24.114751
88	React Native	\N	2025-11-03 19:33:24.114753
89	Vue.js	\N	2025-11-03 19:33:24.114755
90	Angular	\N	2025-11-03 19:33:24.114757
91	PHP	\N	2025-11-03 19:33:24.11476
92	Laravel	\N	2025-11-03 19:33:24.114762
93	Django	\N	2025-11-03 19:33:24.114764
94	Flask	\N	2025-11-03 19:33:24.114766
95	PostgreSQL	\N	2025-11-03 19:33:24.114768
96	MongoDB	\N	2025-11-03 19:33:24.114771
97	AWS	\N	2025-11-03 19:33:24.114773
98	Docker	\N	2025-11-03 19:33:24.114775
99	Kubernetes	\N	2025-11-03 19:33:24.114777
100	CI/CD	\N	2025-11-03 19:33:24.114779
101	Git	\N	2025-11-03 19:33:24.114781
102	Agile Methodology	\N	2025-11-03 19:33:24.114783
103	Photoshop	\N	2025-11-03 19:33:24.114786
104	Illustrator	\N	2025-11-03 19:33:24.114788
105	InDesign	\N	2025-11-03 19:33:24.11479
106	Premiere Pro	\N	2025-11-03 19:33:24.114792
107	Final Cut Pro	\N	2025-11-03 19:33:24.114794
108	WordPress	\N	2025-11-03 19:33:24.114796
109	Shopify	\N	2025-11-03 19:33:24.114798
110	Webflow	\N	2025-11-03 19:33:24.114801
111	Squarespace	\N	2025-11-03 19:33:24.114804
112	Email Marketing	\N	2025-11-03 19:33:24.114806
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.users (id, email, password_hash, first_name, last_name, phone, avatar_url, bio, role, is_active, is_verified, verification_token, reset_token, reset_token_expires, created_at, updated_at, last_login) FROM stdin;
20	admin@reelbrief.com	scrypt:32768:8:1$tB9iNDGCnWjYdQyg$3295dd6e7146557c810a9ee4ff5ceda1ef87e4e588c8302abcbec599b4f1239cb33dfc41cf57d9c337c55c30919aeb240ab9e4c61a9ccd31327b8b4116364c1d	Admin	User	\N	\N	Platform administrator ensuring smooth operations.	admin	t	t	\N	\N	\N	2025-11-03 19:33:28.105538	2025-11-03 19:33:28.105545	\N
21	sarah@techstartup.com	scrypt:32768:8:1$pTFnM30dYzrt8MXN$77c3d41dffbc30e2a4c6e28dd4087c75228baa8469afe41340e7ac5a2abe2558305ef27901716c3acea7320bdd34fa6f67cec0907dd1a17bd9e09ae7abbf67bf	Sarah	Johnson	\N	\N	Building innovative products that change the world.	client	t	t	\N	\N	\N	2025-11-03 19:33:29.125281	2025-11-03 19:33:29.125289	\N
22	mike@creativeagency.com	scrypt:32768:8:1$tmrrkWY8Hn0DZdQ9$6a2252039002f6a08ca152976f3d7c8fb7e5d5c97afb0aa6c7f7644bffee882d0e9cdd1e38b4c192f59e39f7d004a4179fa839c7a59a7e4c13ffc98736aea80d	Mike	Chen	\N	\N	Leading creative campaigns for global brands.	client	t	t	\N	\N	\N	2025-11-03 19:33:30.199326	2025-11-03 19:33:30.199336	\N
23	emma@fashionbrand.com	scrypt:32768:8:1$lCxYolJFzs9JNlVs$a0183ca132eeb91a2c3f6970235a934ccc84bd9dddac427613e88cce3737d5628e1d7f897a7140b9a0a2f761c6724873c092e5c99e25a6909e50a66bc4aa8235	Emma	Rodriguez	\N	\N	Managing fashion brand digital presence and campaigns.	client	t	t	\N	\N	\N	2025-11-03 19:33:31.509273	2025-11-03 19:33:31.509284	\N
24	david@healthtech.com	scrypt:32768:8:1$IvW1KaYGNX4bJOUo$b673b46e76f01bc8e0d42451480ae992b3409dc6532e77efbf18b86e01dc2049e5cc8413b722596241d33ce403341d945aa59f2743fa1b50d0cc6df930322ecb	David	Kim	\N	\N	Leading healthcare technology innovations.	client	t	t	\N	\N	\N	2025-11-03 19:33:32.413735	2025-11-03 19:33:32.41375	\N
25	lisa@edtech.org	scrypt:32768:8:1$TNoL4ltdwN71Vb6K$ddc25113e32038e68d1a94a001a639bab7f0591fcaae8d69ee0760e93a8a51b1f46680f1bc7b31d703a21c9a414c8d7eb9f1979c6e4627ad95c913f80c1f7698	Lisa	Wang	\N	\N	Transforming education through technology.	client	t	t	\N	\N	\N	2025-11-03 19:33:33.510787	2025-11-03 19:33:33.510795	\N
26	james@fintech.io	scrypt:32768:8:1$wwlqiGEezZLQRX8n$a87210c4f8aea9a479bec216d24d158d89a6278aea7fb93d584b639019e7b99fee5f4a0a9ad1eaa2b172218bcbafe2f490959e6e117e4b48d926892da107056b	James	Anderson	\N	\N	Driving financial technology innovation.	client	t	t	\N	\N	\N	2025-11-03 19:33:35.11296	2025-11-03 19:33:35.112968	\N
27	alex@designer.com	scrypt:32768:8:1$GDv8w8Fij4gsjXlX$13d788e2150b8ee20472962fbd0d249573fb7fcae34ae0d458d7f758be94bd32ed120a7b9ce4a3364f5cc7134fe33f10df140605a5e45fab7579b11adbaadc31	Alex	Thompson	\N	\N	Passionate UI/UX designer with 5+ years experience creating beautiful, user-centered digital experiences.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:35.93602	2025-11-03 19:33:35.936028	\N
28	priya@developer.com	scrypt:32768:8:1$uUMhieB49tzwDarw$04b5d293708fd21cf6415e30c65e5598f573263d0935d1e3f57d74412702874f9ad32a59379042bfdf183df583ddafa28b5ed0601daaf5cf8236668306d84e01	Priya	Patel	\N	\N	Full-stack developer specializing in React and Node.js, with a passion for video production.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:38.221592	2025-11-03 19:33:38.221603	\N
29	carlos@animator.com	scrypt:32768:8:1$VWJmu3ECPWeJxxfa$48c79f7b9f2d212384e6b178519d2fee07f69a26ef0298f0ccc6c5c5c9728daf44d6c69c988ea48fad85cf603b9931d64ff6f8e80f2aa4ef7dba20c3c19b43ac	Carlos	Martinez	\N	\N	3D animator and motion graphics artist bringing ideas to life through stunning visuals.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:40.896081	2025-11-03 19:33:40.896093	\N
30	lisa@writer.com	scrypt:32768:8:1$BpGX5N8XoYTXaZzX$2eec37038555960e92e3faf0f36337d0833030afe636df0d91430e532bf3328a549474af958d3b51520989519186c5e0d0b834f5b1b920b54c37dc5dd3c0ef45	Lisa	Zhang	\N	\N	Content writer and copywriter crafting compelling stories that convert.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:43.13655	2025-11-03 19:33:43.136559	\N
31	sophia@marketing.com	scrypt:32768:8:1$ngPFVIKfPM3iPOeI$e2ec69921bb5cfbdcbfb700846fe1135e5527dc7fca44badec526e16bbd5c0d8d096c16e7cc53057e3e5e846aa6eec86b5bec417df86253881020147baece4ba	Sophia	Garcia	\N	\N	Digital marketing expert helping brands grow their online presence.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:45.392498	2025-11-03 19:33:45.392505	\N
32	marcus@mobile.dev	scrypt:32768:8:1$OSD4F7UHh5ga2UEW$448f40d305d19dd8a20d9b4026f7ec1a47303d93b89efaa04226f57a1d8d97cf50323e9b86a965e6344a327065f776e8b7a603c57806d61632a5cf17d697d822	Marcus	Johnson	\N	\N	Mobile app developer specializing in React Native and Flutter cross-platform solutions.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:47.233371	2025-11-03 19:33:47.233382	\N
33	natalie@graphics.com	scrypt:32768:8:1$1raSwCOoBwtUAFPP$91c5d4834a9b53c247662eac1b8ad3ca1376641e78668e35ef02d9f864d0892d5e74184f2f574dad0a6b6ba11d6b22068dedfecbdaf3e93d1b184d67a83dc519	Natalie	Chen	\N	\N	Graphic designer and illustrator with a passion for branding and visual identity.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:49.514661	2025-11-03 19:33:49.514674	\N
34	ryan@videopro.com	scrypt:32768:8:1$5Ep1l9dgWyYbJ2oS$40cb65dbc5ee23ff995ec02ea209a443a46b973f444afa478aa7a56b421093f1aeb3aad21ef79ae3b9987f91aacad84121b0a0f5067be1ade6623929adca9ab3	Ryan	O'Connor	\N	\N	Professional video editor and filmmaker with expertise in Premiere Pro and After Effects.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:53.175494	2025-11-03 19:33:53.17551	\N
35	taylor@fullstack.io	scrypt:32768:8:1$gVQiKRWXjg1Ia1ID$82b3f33327c4d7d8096f4e5443e8aadd1d3d0e6f4a2c394db9ac0bb48a96af05ddad327c3a9f6ada1a6195eb953c34e7d6183add0fb40e5116cf93b02994f3b9	Taylor	Brown	\N	\N	Full-stack developer with expertise in modern web technologies and cloud infrastructure.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:55.424742	2025-11-03 19:33:55.424753	\N
36	isabella@content.co	scrypt:32768:8:1$cSakH1ki2bMZg7mn$4828ed4b7ee823806a661198478b302b4eedf7c0e199bd1c86866e9fb472ba59900a2f6a1927b81e455be1f3cf73f3361bd5b1c90082eb08a59b9ec3c102696c	Isabella	Rossi	\N	\N	Content strategist and SEO specialist helping brands improve their online presence.	freelancer	t	t	\N	\N	\N	2025-11-03 19:33:58.297588	2025-11-03 19:33:58.2976	\N
37	kevin@devops.tech	scrypt:32768:8:1$T0jBBgM7tDPXK7dH$ef9f1359d91c8214dcbd51d2f91ccc12ebad19fd0a174e8b7028ce9e42dec7b741de9cc3f5ff81103d49606bdb79f1c1846d6d4951822c9c23cc19d37cfa98e0	Kevin	Nguyen	\N	\N	DevOps engineer specializing in cloud infrastructure, CI/CD, and system architecture.	freelancer	t	t	\N	\N	\N	2025-11-03 19:34:00.748996	2025-11-03 19:34:00.749005	\N
38	olivia@uiux.design	scrypt:32768:8:1$R9A9hnDmLeqgYFch$b195882df9bdcbaf1b058fa649570870e08e7e0ff6ddaad819fc7b25fdfba9e2ae243ad610b7616270532ca4af50792b4ef211a5795715ec4f27532a0c89edd6	Olivia	Park	\N	\N	UI/UX designer focused on creating intuitive and accessible digital experiences.	freelancer	t	t	\N	\N	\N	2025-11-03 19:34:03.002475	2025-11-03 19:34:03.002484	\N
\.


--
-- Data for Name: wallet_transactions; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.wallet_transactions (id, wallet_id, amount, transaction_type, description, reference_id, created_at) FROM stdin;
\.


--
-- Data for Name: wallets; Type: TABLE DATA; Schema: public; Owner: reelbrief_user
--

COPY public.wallets (id, user_id, balance, currency, created_at, updated_at) FROM stdin;
\.


--
-- Name: activity_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.activity_logs_id_seq', 1, false);


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

SELECT pg_catalog.setval('public.freelancer_profiles_id_seq', 24, true);


--
-- Name: freelancer_skills_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.freelancer_skills_id_seq', 112, true);


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

SELECT pg_catalog.setval('public.skills_id_seq', 112, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.users_id_seq', 38, true);


--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.wallet_transactions_id_seq', 1, false);


--
-- Name: wallets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: reelbrief_user
--

SELECT pg_catalog.setval('public.wallets_id_seq', 1, false);


--
-- Name: activity_logs activity_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_pkey PRIMARY KEY (id);


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
-- Name: wallet_transactions wallet_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_user_id_key; Type: CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_key UNIQUE (user_id);


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
-- Name: idx_user_unread; Type: INDEX; Schema: public; Owner: reelbrief_user
--

CREATE INDEX idx_user_unread ON public.notifications USING btree (user_id, is_read);


--
-- Name: activity_logs activity_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.activity_logs
    ADD CONSTRAINT activity_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


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
-- Name: projects fk_projects_approved_by; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT fk_projects_approved_by FOREIGN KEY (approved_by) REFERENCES public.users(id);


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
-- Name: wallet_transactions wallet_transactions_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.wallets(id);


--
-- Name: wallets wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: reelbrief_user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON SEQUENCES TO reelbrief_user;


--
-- Name: DEFAULT PRIVILEGES FOR TYPES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TYPES TO reelbrief_user;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON FUNCTIONS TO reelbrief_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: -; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT ALL ON TABLES TO reelbrief_user;


--
-- PostgreSQL database dump complete
--

\unrestrict eeTlPo4J84Xb2Ya64H8DbGiMQOjKuCFCT2BIrFx4g4B8ohAzapWU7uNHPnT61bT

