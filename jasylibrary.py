
import glob, os
import jasy.item.Class
import jasy.item.Asset
import jasy.item.Abstract


@itemtype("template", "Templates")
class TemplateItem(jasy.item.Abstract.AbstractItem):
	kind = "template"

	def generateId(self, relpath, package):
		if package:
			fileId = "%s/" % package
		else:
			fileId = ""

		fileId =  (fileId + os.path.splitext(relpath)[0]).replace("/", ".").split(".")

		last = len(fileId) - 1
		name = fileId[last]
		fileId[last] = name[0].upper() + name[1:]
		
		return ".".join(fileId)



@postscan()
def postscan():
	virtualProject = session.getVirtualProject()
	for project in session.getProjects():
		items = project.getItems("template.Template")
		if items:
			for name in items.keys():
				item = items[name]
				cls = virtualProject.getItem("jasy.Class", item.getId())

				if cls is None:
					cls = jasy.item.Class.ClassItem(project, item.getId())
					virtualProject.addItem("jasy.Class", cls)

				if cls.mtime != item.mtime:
					cls.mtime = item.mtime
					
					cls.setTextFilter(templateFilter)

					#filePath = os.path.join(virtualProject.getPath(), "src", item.getId().replace(".", os.sep)) + ".js"
					#cls.saveText(js, filePath)


def templateFilter(text, item):
	js = """
		core.Module("%(name)s", {
			get : function() {
				return core.template.Compiler.compile("%(content)s");
			}
		});
	""" % {
		"name": item.getId(),
		"content" : escapeContent(text)
	}
	return js

def escapeContent(content):
	return content.replace("\"", "\\\"").replace("\n", "\\n")