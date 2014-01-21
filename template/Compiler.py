/*
==================================================================================================
  Core - JavaScript Foundation
  Copyright 2010-2012 Zynga Inc.
  Copyright 2012-2013 Sebastian Werner
--------------------------------------------------------------------------------------------------
  Based on the work of:
  Hogan.JS by Twitter, Inc.
  https://github.com/twitter/hogan.js
  Licensed under the Apache License, Version 2.0
  http://www.apache.org/licenses/LICENSE-2.0
==================================================================================================
*/

"use strict";

(function ()
{
	var escapeMatcher = /[\\\"\n\r]/g;

	var escapeMap = {
		"\\" : '\\\\',
		"\"" : '\\\"',
		"\n" : '\\n',
		"\r" : '\\r'
	};

	var escapeReplacer = function(str) {
		return escapeMap[str];
	};

	var accessTags =
	{
		"#" : 1, // go into section / loop start
		"?" : 1, // if / has
		"^" : 1, // if not / has not
		"$" : 1, // insert variable
		"=" : 1  // insert raw / non escaped
	};

	// Tags which support children
	var innerTags =
	{
		"#" : 1,
		"?" : 1,
		"^" : 1
	};

	function walk(node, labels, nostrip)
	{
		var code = '';

		for (var i=0, l=node.length; i<l; i++)
		{
			var current = node[i];
			var tag = current.tag;

			if (tag == null)
			{
				code += 'buf+="' + current.replace(escapeMatcher, escapeReplacer) + '";';
			}
			else if (tag == '\n')
			{
				code += 'buf+="\\n";';
			}
			else
			{
				var name = current.name;
				var escaped = name.replace(escapeMatcher, escapeReplacer);

				if (tag in accessTags)
				{
					var accessor = name == "." ? 2 : ~name.indexOf('.') ? 1 : 0;
					var accessorCode = '"' + escaped + '",' + accessor + ',data';

					if (tag in innerTags) {
						var innerCode = walk(current.nodes, labels, nostrip);
					}

					if (tag == '?') {
						code += 'if(this._has(' + accessorCode + ')){' + innerCode + '}';
					} else if (tag == '^') {
						code += 'if(!this._has(' + accessorCode + ')){' + innerCode + '}';
					} else if (tag == '#') {
						code += 'this._section(' + accessorCode + ',partials,labels,function(data,partials,labels){' + innerCode + '});';
					} else if (tag == '=') {
						code += 'buf+=this._data(' + accessorCode + ');';
					} else if (tag == '$') {
						code += 'buf+=this._variable(' + accessorCode + ');';
					}
				}
				else if (tag == '>')
				{
					code += 'buf+=this._partial("' + escaped + '",data,partials,labels);';
				}
				else if (tag == '_')
				{
					// Support either static labels and dynamic labels
					var resolved = labels && labels[escaped];
					if (typeof resolved == "string") {
						code += walk(core.template.Parser.parse(resolved, true), labels);
					} else {
						code += 'buf+=this._label("' + escaped + '",data,partials,labels);';
					}
				}
			}
		}

		return code;
	}


	/**
	 * This is the Compiler of the template engine and transforms the token tree into a compiled template instance.
	 */
	core.Module("core.template.Compiler",
	{
		/**
		 * {core.template.Template} Translates the @code {Array} tree from {core.template.Parser#parse} into actual JavaScript
		 * code (in form of a {core.template.Template} instance) to insert dynamic data fields. It uses
		 * the original @text {String} for template construction. There is also the possibility to inject
		 * static @labels {Map} at compile time level or resolve them dynamically at every rendering.
		 * Optionally you can keep white spaces (line breaks, leading, trailing, etc.) by
		 * enabling @nostrip {Boolean?false}. Additionally one can define a template @name {String} for
		 * improved debugging capabilities.
		 */
		compile : function(text, labels, nostrip, name)
		{
			var tree = core.template.Parser.parse(text, nostrip);
			var wrapped = 'var buf="";' + walk(tree, labels, nostrip) + 'return buf;';

			return new core.template.Template(new Function('data', 'partials', 'labels', wrapped), text, name);
		}
	});
})();
