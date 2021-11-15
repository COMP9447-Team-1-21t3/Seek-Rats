// The module 'vscode' contains the VS Code extensibility API
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {

	const fs = require('fs');
	const path = require('path');
	const toml = require('toml');
	const config = toml.parse(fs.readFileSync(path.join(__dirname, 'regex.toml'), 'utf-8'));
	const rules = config.rules;
		
	let timeout: NodeJS.Timeout | undefined = undefined;

	// create a decorator type that we use to decorate secrets
	const SecretsFoundInCodeDecorationType = vscode.window.createTextEditorDecorationType({
			cursor: 'crosshair',
			backgroundColor: { id: 'secretscanner.secretBackground' }
			
	});

	let activeEditor = vscode.window.activeTextEditor;

	function updateDecoration(regEx: RegExp, description: string) {
			if (!activeEditor) {
					return;
			}
			const text = activeEditor.document.getText();
			const SecretsFoundInCode = [];
			let match;
			while ((match = regEx.exec(text))) {
					const startPos = activeEditor.document.positionAt(match.index);
					const endPos = activeEditor.document.positionAt(match.index + match[0].length);
					const decoration = { range: new vscode.Range(startPos, endPos), hoverMessage: '**' + description + '**' };
					SecretsFoundInCode.push(decoration);
			}
			activeEditor.setDecorations(SecretsFoundInCodeDecorationType, SecretsFoundInCode);
	}

	function updateDecorations() {
			if (!activeEditor) {
					return;
			}
			rules.forEach((element: { regex: string | RegExp; description: string; }) => {
					let re = new RegExp(element.regex, "g");
					updateDecoration(re, element.description);
			});
	}

	function triggerUpdateDecorations() {
			if (timeout) {
					clearTimeout(timeout);
					timeout = undefined;
			}
			timeout = setTimeout(updateDecorations, 500);
	}

	if (activeEditor) {
			triggerUpdateDecorations();
	}

	let disposable = vscode.commands.registerCommand('secretscanner.scan', () => {
		triggerUpdateDecorations();
	});

	context.subscriptions.push(disposable);
}

export function deactivate() {}
