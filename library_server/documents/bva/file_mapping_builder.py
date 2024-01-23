from knowpy.misc.jsonld_lib import *
from knowpy.misc.doc_reader import *

document_list = get_document_list('./')

file_mapping = [
	{
		"@id": DOC_PREFIX+get_uri_from_txt(doc.replace(' ','_')),
		"my:url": f"https://search.usa.gov/search?affiliate=bvadecisions&sort_by=&query={doc.replace('.txt','')}",
		HAS_LABEL_PREDICATE: f"Citation Nr: {doc.replace('.txt','')}"
	}
	for doc in map(os.path.basename,document_list)
	if doc.endswith('.txt')
]

with open('file_mapping.kg.json', 'w') as f:
	json.dump(file_mapping, f, indent=4)
