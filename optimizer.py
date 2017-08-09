#! /usr/bin/env python
import os
import itertools
import subprocess
import json

def get_all_source_files(folder, extensions):
	sources = []
	for root, dirs, files in os.walk(folder):
		for f in files:
			for ext in extensions:
				if f.endswith(ext):
				     sources.append(os.path.join(root, f))
	return sources

def write_configuration_file(folder, values):

	filename = os.path.join(folder, '.clang-format')
	with open(filename, 'w') as f:
		f.write('---\n')
		f.write('Language: Cpp\n')

		firstBraceWrapping = True

		for k in sorted(values):
			if k.startswith('BraceWrapping'):
				if firstBraceWrapping:
					f.write('BraceWrapping:\n')
					firstBraceWrapping = False
				name = k.replace('BraceWrapping', '')
				f.write('  ' + name + ': ' + str(values[k]) + '\n')
			else:
				f.write(k + ': ' + str(values[k]) + '\n')

		f.write('...\n')

def run_clang_format(clang_format, folder, filename):
	p = subprocess.Popen( [clang_format, '-style=file', '-i', filename], shell=False, cwd=folder)

def git_diff_stat(folder):
	p = subprocess.Popen( ['git', 'diff', '--shortstat'], cwd=folder, stdout=subprocess.PIPE)
	return p.communicate()[0]
	


if __name__ == "__main__":

	mapping = dict()
	#mapping['BasedOnStyle']=['LLVM', 'Google', 'Chromium', 'Mozilla', 'Webkit']
	mapping['AccessModifierOffset']=list(range(-4,4))
	mapping['AlignAfterOpenBracket']=['Align', 'DontAlign', 'AlwaysBreak']
	mapping['AlignConsecutiveAssignments']=['true', 'false']
	mapping['AlignConsecutiveDeclarations']=['true', 'false']
	mapping['AlignEscapedNewlinesLeft']=['true', 'false']
	mapping['AlignOperands']=['true', 'false']
	mapping['AlignTrailingComments']=['true', 'false']
	mapping['AllowAllParametersOfDeclarationOnNextLine']=['true', 'false']
	mapping['AllowShortBlocksOnASingleLine']=['true', 'false']
	mapping['AllowShortCaseLabelsOnASingleLine']=['true', 'false']
	mapping['AllowShortFunctionsOnASingleLine']=['None', 'Empty', 'Inline', 'All']
	mapping['AllowShortIfStatementsOnASingleLine']=['true', 'false']
	mapping['AllowShortLoopsOnASingleLine']=['true', 'false']
	mapping['AlwaysBreakAfterDefinitionReturnType']=['None', 'All', 'TopLevel']
	mapping['AlwaysBreakAfterReturnType']=['None', 'All', 'TopLevel', 'AllDefinitions', 'TopLevelDefinitions']
	mapping['AlwaysBreakBeforeMultilineStrings']=['true', 'false']
	mapping['AlwaysBreakTemplateDeclarations']=['true', 'false']
	mapping['BinPackArguments']=['true', 'false']
	mapping['BinPackParameters']=['true', 'false']
	mapping['BraceWrappingAfterClass']=['true', 'false']
	mapping['BraceWrappingAfterControlStatement']=['true', 'false']
	mapping['BraceWrappingAfterEnum']=['true', 'false']
	mapping['BraceWrappingAfterFunction']=['true', 'false']
	mapping['BraceWrappingAfterNamespace']=['true', 'false']
	mapping['BraceWrappingAfterStruct']=['true', 'false']
	mapping['BraceWrappingAfterUnion']=['true', 'false']
	mapping['BraceWrappingBeforeCatch']=['true', 'false']
	mapping['BraceWrappingBeforeElse']=['true', 'false']
	mapping['BraceWrappingIndentBraces']=['true', 'false']
	mapping['BreakBeforeBinaryOperators']=['None', 'NonAssignment', 'All']
	mapping['BreakBeforeTernaryOperators']=['true', 'false']

	combination=itertools.product(*mapping.values())

	extensions = ['.cpp', '.cxx', '.c', '.hpp', '.hxx', '.h']
	folder='/home/agelas/dev/formatting/telemetry'

	sources = get_all_source_files(folder, extensions)

	result = []

	j = 0
	keys = mapping.keys()
	number_parameters = len(keys)

	for element in combination:
		print('generate .clang-format file!')
		values=dict()

		for i in range(number_parameters):
			values[keys[i]] = element[i]

		write_configuration_file(folder, values)

		print('reformat ' + folder)
		
		for f in sources:
			run_clang_format('clang-format-4.0', folder, f)


		stat = git_diff_stat(folder)		
		metric = [int(s) for s in stat.split() if s.isdigit()]
		
		output = dict()
		output['config'] = values
		output['metric'] = dict()
		output['metric']['insertions'] = metric[1]
		output['metric']['deletions'] = metric[2]
		output['metric']['sum'] = metric[1] + metric[2]

		result.append(output)

		j = j + 1
		if j == 2:
			break

	with open('result.json', 'w') as fp:
		json.dump(result, fp, indent=4, sort_keys=True)

		#	for k in mapping.keys():
		#		print(
		#	print(mapping.keys()[0] + ": " + str(element[len(element) - 1]))
		#	break

