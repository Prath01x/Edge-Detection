extensions=`code --list-extensions`

if [[ $extensions == *"cpptools"* ]]; then
    echo "Extension cpp-tools already installed."
    exit 0
fi

# install the extension
echo "Installing extension cpp-tools..."
wget https://github.com/microsoft/vscode-cpptools/releases/download/1.3.1/cpptools-linux.vsix
code --install-extension cpptools-linux.vsix
rm cpptools-linux.vsix
exit 0