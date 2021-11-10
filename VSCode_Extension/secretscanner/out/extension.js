"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = void 0;
const vscode = require("vscode");

function activate(context) {
    console.log('decorator sample is activated');
    const fs = require('fs');
    const path = require('path');
    const toml = require('toml');
    const config = toml.parse(fs.readFileSync(path.join(__dirname, 'regex.toml'), 'utf-8'));
    const rules = config.rules;

    let timeout = undefined;
    // create a decorator type that we use to decorate small numbers
    const smallNumberDecorationType = vscode.window.createTextEditorDecorationType({
        borderWidth: '1px',
        borderStyle: 'solid',
        overviewRulerColor: 'blue',
        overviewRulerLane: vscode.OverviewRulerLane.Right,
        light: {
            // this color will be used in light color themes
            borderColor: 'darkblue'
        },
        dark: {
            // this color will be used in dark color themes
            borderColor: 'lightblue'
        }
    });
    // create a decorator type that we use to decorate large numbers
    const SecretsFoundInCodeDecorationType = vscode.window.createTextEditorDecorationType({
        cursor: 'crosshair',
        backgroundColor: { id: 'myextension.largeNumberBackground' }
    });
    let activeEditor = vscode.window.activeTextEditor;

    function updateDecoration(regEx) {
        console.log(regEx);
        if (!activeEditor) {
            return;
        }
        const text = activeEditor.document.getText();
        const SecretsFoundInCode = [];
        let match;
        while ((match = regEx.exec(text))) {
            const startPos = activeEditor.document.positionAt(match.index);
            const endPos = activeEditor.document.positionAt(match.index + match[0].length);
            const decoration = { range: new vscode.Range(startPos, endPos), hoverMessage: 'Secret **' + match[0] + '**' };
            SecretsFoundInCode.push(decoration);
        }
        activeEditor.setDecorations(SecretsFoundInCodeDecorationType, SecretsFoundInCode);
    }
    function updateDecorations() {
        if (!activeEditor) {
            return;
        }
        rules.forEach((element) => {
            let re = new RegExp(element.regex, "g");
            updateDecoration(re);
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
exports.activate = activate;
//# sourceMappingURL=extension.js.map
