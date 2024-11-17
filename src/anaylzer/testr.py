import tkinter as tk
from tkinter import messagebox
from tkinterweb import HtmlFrame

class ACEEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ACE Editor Example")

        # Button to open the ACE Editor
        self.open_button = tk.Button(root, text="Open ACE Editor", command=self.open_ace_editor)
        self.open_button.pack(pady=10)

    def open_ace_editor(self):
        # Create a new window for the ACE Editor
        ace_editor_window = tk.Toplevel(self.root)
        ace_editor_window.title("ACE Editor")

        # Create an HTML Frame for ACE Editor
        ace_frame = HtmlFrame(ace_editor_window, width=800, height=600)
        ace_frame.pack()

        # HTML to load the ACE Editor
        ace_html = """
        <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js"></script>
            </head>
            <body>
                <div id="editor" style="height: 100%; width: 100%;"></div>
                <script type="text/javascript">
                    var editor = ace.edit("editor");
                    editor.setTheme("ace/theme/monokai");
                    editor.session.setMode("ace/mode/json");
                    editor.setValue('{"key": "value", "nested": [1, 2, 3]}', -1); // Default JSON structure

                    // Function to send data back to Python (via window.postMessage)
                    function getEditorContent() {
                        return editor.getValue();
                    }
                </script>
            </body>
        </html>
        """

        # Load the HTML content into the frame
        ace_frame.load_html(ace_html)

        # Add a button to get the editor content
        get_content_button = tk.Button(ace_editor_window, text="Get Content", command=lambda: self.get_content_from_ace(editor))
        get_content_button.pack(pady=10)

    def get_content_from_ace(self, editor):
        # This is where you'd extract the content from the ACE editor
        editor_content = editor.getValue()
        print("Editor Content:", editor_content)

        # Optionally, process or validate the content (e.g., JSON)
        try:
            parsed_content = json.loads(editor_content)
            messagebox.showinfo("Parsed Content", f"Content is valid JSON: {parsed_content}")
        except json.JSONDecodeError:
            messagebox.showerror("Invalid JSON", "The content is not valid JSON.")

# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ACEEditorApp(root)
    root.mainloop()
