from enum import Enum

class TokenType(Enum):
	open = 1
	close = 2
	string = 4

class Token:
	def __init__(self, ttype, value=None):
		self.type = ttype
		self.value = value
	
	def __str__(self):
		return "{} ({})".format(self.type, self.value)

def token_generator(file, encoding=None):
	with open(file, "r", encoding=encoding) as fp:
		buf = []
		in_string = False
		while True:
			c = fp.read(1)
			if c == "":
				break
			elif c == "/":
				if fp.read(1) == "/":
					fp.readline()
			elif c == "{":
				yield Token(TokenType.open)
			elif c == "}":
				yield Token(TokenType.close)
			elif c == "\"":
				if in_string:
					yield Token(TokenType.string, "".join(buf))
					buf = []
				in_string = not in_string
			elif in_string:
				buf.append(c)

def parse(file, encoding=None):
	obj = {}
	obj_stack = []
	key = None
	for token in token_generator(file, encoding=encoding):
		if token.type == TokenType.open:
			new_obj = {}
			obj[key] = new_obj
			obj_stack.append(obj)
			obj = new_obj
			key = None
		elif token.type == TokenType.close:
			obj = obj_stack.pop()
		elif token.type == TokenType.string:
			if not key:
				key = token.value
			elif obj is not None:
				obj[key] = token.value
				key = None
	return obj

def write(file, obj, comment=None):
	def list_as_dict(val):
		return {i+1:val[i] for i in range(0, len(val))}
	
	with open(file, "w") as out:
		def write_obj(obj_key, obj, indent=0):
			indent_str = "\t"*indent
			
			if isinstance(obj_key, str):
				if obj_key.startswith("_"):
					return
				obj_key = obj_key[:1].upper()+obj_key[1:]
			out.write("{}\"{}\"\n{}{{\n".format(indent_str, obj_key, indent_str))
			
			for key in sorted(obj.keys()):
				val = obj[key]
				if isinstance(val, dict):
					write_obj(key, val, indent+1)
				elif isinstance(val, list):
					write_obj(key, list_as_dict(val), indent+1)
				elif isinstance(val, object) and hasattr(val, "__dict__"):
					if hasattr(val, "kv1_comment"):
						c = val.kv1_comment()
						if c is not None:
							for line in c.split("\n"):
								out.write("{}\t// {}\n".format(indent_str, line))
					write_obj(key, val.__dict__, indent+1)
				else:
					if isinstance(key, str):
						if key.startswith("_"):
							continue
						key = key[:1].upper()+key[1:]
					out.write("{}\t\"{}\"\t\"{}\"\n".format(indent_str, key, val))
			out.write("{}}}\n".format(indent_str))
		
		if comment:
			out.write("// {}\n".format(comment))
		for key in obj.keys():
			val = obj[key]
			if isinstance(val, dict):
				write_obj(key, val)
			elif isinstance(val, list):
				write_obj(key, list_as_dict(val))
