import React, { useState, useContext, useEffect } from "react";
import Editor from "@ckeditor/ckeditor5-build-classic";
import { CKEditor } from "@ckeditor/ckeditor5-react";
import { AuthContext } from "@/context/authContext";

const CKEditorComponent: React.FC = () => {
  const { apiKey } = useContext(AuthContext);
  const [editorData, setEditorData] = useState("");

  const extractSentences = (text: string) => {
    const plainText = text.replace(/<\/?[^>]+(>|$)/g, "");
    const sentences = plainText.match(/[^.!?]+[.!?]*/g) || [];
    return sentences;
  };

  const logSentences = (data: string) => {
    const sentences = extractSentences(data);
    console.log("Sentences:", sentences);
  };

  useEffect(() => {
    console.log("apiKey has changed, CKEditor will reinitialize.");
    console.log(apiKey);
  }, [apiKey]);

  return (
    <div>
      <CKEditor
        key={apiKey}
        editor={Editor}
        data=""
        config={{
          placeholder: "Type your content here...",
          apiKey: apiKey || "",
        }}
        onReady={(editor) => {
          console.log("Editor is ready to use!", editor);
        }}
        onChange={(event, editor) => {
          const data = editor.getData();
          setEditorData(data);
          logSentences(data);
          console.log(data);
        }}
        onBlur={(event, editor) => {
          console.log("Blur.", editor);
        }}
        onFocus={(event, editor) => {
          console.log("Focus.", editor);
        }}
      />
      <style jsx global>{`
        .ck-editor__editable_inline {
          min-height: 20rem;
        }
      `}</style>
    </div>
  );
};

export default CKEditorComponent;
