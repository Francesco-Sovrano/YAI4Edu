from bottle import run, get, post, route, hook, request, response, static_file
from random import random
import sys
import uuid
import json
port = int(sys.argv[1])
algorithm = sys.argv[2] if len(sys.argv)>2 else None

###############################################################
# CORS

@route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
	"""
	This route takes priority over all others. So any request with an OPTIONS
	method will be handled by this function.

	See: https://github.com/bottlepy/bottle/issues/402

	NOTE: This means we won't 404 any invalid path that is an OPTIONS request.
	"""
	add_cors_headers()

@hook('after_request')
def enable_cors_after_request_hook():
	"""
	This executes after every route. We use it to attach CORS headers when
	applicable.
	"""
	add_cors_headers()

def add_cors_headers():
	try:
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
	except Exception as e:
		print('Error:',e)

###############################################################
# Static Routes

@get("/favicon.ico")
def favicon():
	return static_file("favicon.ico", root="static/img/")

###################################

@get("/resources/static/excerpts/<filepath:re:.*>")
def docs(filepath):
	return static_file(filepath, root="../oke/documents/edu/excerpts/")

@get("/resources/static/pdf/<filepath:re:.*>")
def docs(filepath):
	return static_file(filepath, root="../oke/documents/pdf/")

@get("/resources/static/component/<filepath:re:.*>")
def docs(filepath):
	return static_file(filepath, root="static/component/")

###################################

@get("/resources/static/<filepath:re:.*\.css>")
def css(filepath):
	return static_file(filepath, root="static/css/")

@get("/resources/static/<filepath:re:.*\.(eot|otf|svg|ttf|woff|woff2?)>")
def font(filepath):
	return static_file(filepath, root="static/css/")

@get("/resources/static/<filepath:re:.*\.(jpg|png|gif|ico|svg)>")
def img(filepath):
	return static_file(filepath, root="static/img/")

@get("/resources/static/<filepath:re:.*\.js>")
def js(filepath):
	return static_file(filepath, root="static/js/")

@get("/resources/static/<filepath:re:.*\.vue>")
def js(filepath):
	return static_file(filepath, root="static/js/")

@get("/resources/static/<filepath:re:.*\.json>")
def js(filepath):
	return static_file(filepath, root="static/json/")

# @get("/documents/<filepath:re:.*\.pdf>")
# def docs(filepath):
# 	return static_file(filepath, root="../oke/documents/")

@get("/<filepath:re:.*\.html>")
def html(filepath):
	print(filepath)
	return static_file(filepath, root="static/html/")

@get("/")
def home():
	resp = static_file(f"index_{algorithm}.html" if algorithm else "index.html", root="static/html/")
	if not request.get_cookie("uuid"):
		user_uid = str(uuid.uuid4())#.int
		resp.set_cookie("uuid", user_uid)
	# 	print('new',user_uid)
	# else:
	# 	print('old',request.get_cookie("uuid"))
	return resp

@post("/submission")
def submission():
	user_uid = request.get_cookie("uuid")
	results_dict = json.loads(request.forms.get('results_dict'))
	# print(json.dumps(results_dict, indent=4))
	print(user_uid, 'is submitting', results_dict)
	with open(f"results/{'_'.join(map(str,[algorithm if algorithm else 'yai', 'memorandum', user_uid, random()]))}.json", 'w') as f:
		json.dump(results_dict, f, indent=4)

if __name__ == "__main__":
	run(server='meinheld', host='0.0.0.0', port=port, debug=False)
	# run(server='tornado', host='0.0.0.0', port=port, debug=False)
	