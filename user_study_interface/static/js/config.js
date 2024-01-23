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
	}
];
KNOWN_KNOWLEDGE_GRAPH = format_jsonld(KNOWN_KNOWLEDGE_GRAPH);
KNOWN_ENTITY_DICT = get_typed_entity_dict_from_jsonld(KNOWN_KNOWLEDGE_GRAPH);
// console.log(KNOWN_ENTITY_DICT);
