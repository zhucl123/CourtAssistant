import os
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

def convert_pdfs_to_md(pdfs_name, base_path='./案件'):

    pdfs_folder = os.path.join(base_path, '')
    print(pdfs_folder)
    md_texts = []

    for pdf_name in pdfs_name:
        pdf_file_path = os.path.join(pdfs_folder, pdf_name)
        if not os.path.exists(pdf_file_path):
            print(f"文件 {pdf_name} 不存在")
            continue

        # read bytes
        reader1 = FileBasedDataReader("")
        pdf_bytes = reader1.read(pdf_file_path)  # read the pdf content

        # proc
        ## Create Dataset Instance
        ds = PymuDocDataset(pdf_bytes)

        ## inference
        if ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = ds.apply(doc_analyze, ocr=True)
            ## pipeline
            pipe_result = infer_result.pipe_ocr_mode(FileBasedDataWriter(""))
        else:
            infer_result = ds.apply(doc_analyze, ocr=False)
            ## pipeline
            pipe_result = infer_result.pipe_txt_mode(FileBasedDataWriter(""))

        ### get markdown content
        md_content = pipe_result.get_markdown("")
        md_texts.append(md_content)

    return '\n'.join(md_texts)

# 示例调用
if __name__ == "__main__":
    pdfs_name = ['demo1.pdf']
    md_text = convert_pdfs_to_md(pdfs_name)
    print(md_text)