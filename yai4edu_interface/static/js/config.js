// const EBOOK_SERVER_URL = location.protocol+'//'+location.hostname+':'+location.port+'/';
// console.log('EBOOK_SERVER_URL:', EBOOK_SERVER_URL);
const OKE_SERVER_URL = location.protocol+'//'+location.hostname+':8019/';
console.log('OKE_SERVER_URL:', OKE_SERVER_URL);
const GET_OVERVIEW_API = OKE_SERVER_URL+"overview";
const GET_ANSWER_API = OKE_SERVER_URL+"answer";
const GET_ANNOTATION_API = OKE_SERVER_URL+"annotation";

const BVA_SERVER_URL = location.protocol+'//'+location.hostname+':8021/';
console.log('BVA_SERVER_URL:', BVA_SERVER_URL);
const GET_OVERVIEW_BVA_API = BVA_SERVER_URL+"overview";
const GET_ANSWER_BVA_API = BVA_SERVER_URL+"answer";

OVERVIEW_CACHE = {};
TAXONOMICAL_VIEW_CACHE = {};
ANNOTATION_CACHE = {};
ANNOTATED_HTML_CACHE = {};
KNOWN_KNOWLEDGE_GRAPH = [
	{
		'@id': 'myf:excerpts.akn',
		'@type': 'dbr:Book',
		'my:url': '/resources/static/excerpts/[2013]Excerpts of UNITED STATES LEGAL LANGUAGE AND CULTURE - AN INTRODUCTION TO THE US COMMON LAW SYSTEM.pdf',
		'rdfs:label': 'Excerpts of "United States legal language and culture: An introduction to the US common law system"'
	},
	{
		'@id': 'myf:introduction_to_basic_legal_citation',
		'@type': 'dbr:Book',
		'my:url': '/resources/static/books/pdf/[2013]Introduction to BASIC LEGAL CITATION.pdf',
		'rdfs:label': 'Introduction to Basic Legal Citation'
	},
	{
		'@id': 'myf:law_school_materials_for_success',
		'@type': 'dbr:Book',
		'my:url': '/resources/static/books/pdf/[2013]Law School Materials for Success.pdf',
		'rdfs:label': 'Law School Materials for Success'
	},
	{
		'@id': 'myf:law_101_fundamentals_of_the_law_new_york_law_and_federal_law',
		'@type': 'dbr:Book',
		'my:url': '/resources/static/books/pdf/[2018]LAW 101 FUNDAMENTALS OF THE LAW - NEW YORK LAW AND FEDERAL LAW.pdf',
		'rdfs:label': 'Law 101 Fundamentals of the Law - New York Law and Federal Law'
	},
	{
		'@id': 'myf:sources_of_american_law_an_introduction_to_legal_research',
		'@type': 'dbr:Book',
		'my:url': '/resources/static/books/pdf/[2021]Sources of American Law - An Introduction to Legal Research.pdf',
		'rdfs:label': 'Sources of American Law - An Introduction to Legal Research'
	}
];
KNOWN_KNOWLEDGE_GRAPH = format_jsonld(KNOWN_KNOWLEDGE_GRAPH);
KNOWN_ENTITY_DICT = get_typed_entity_dict_from_jsonld(KNOWN_KNOWLEDGE_GRAPH);
// console.log(KNOWN_ENTITY_DICT);
