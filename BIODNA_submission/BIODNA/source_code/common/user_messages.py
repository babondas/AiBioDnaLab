"""All messages shown to users, kept in one place so they are easy to find and change."""
from source_code.common import config

SUPPORTED_LIST = "Supported formats: " + ", ".join(
    extension[1:].upper() for extension in sorted(config.SUPPORTED_EXTENSIONS)
) + "."

# ---- Check 1: format ----
UNSUPPORTED_MESSAGES = {
    ".docx": "Word documents are not supported. Please save the file as PDF and upload again.",
    ".doc": "Word documents are not supported. Please save the file as PDF and upload again.",
    ".zip": "ZIP files are not supported. Please extract the files and upload them one by one.",
    ".rar": "RAR files are not supported. Please extract the files and upload them one by one.",
    ".png": "Images are not supported. Please upload a PDF that contains real text.",
    ".jpg": "Images are not supported. Please upload a PDF that contains real text.",
    ".jpeg": "Images are not supported. Please upload a PDF that contains real text.",
    ".pptx": "PowerPoint files are not supported. Please save the slides as PDF and upload again.",
}
UNKNOWN_FORMAT = "This file type is not supported."

# ---- Checks 2 and 3: content and size ----
FILE_IS_EMPTY = "The file is empty (0 bytes)."
FILE_TOO_LARGE = f"The file is larger than {config.MAX_FILE_SIZE_MB} MB."

# ---- Check 4: reading ----
PDF_CANNOT_BE_OPENED = "This PDF could not be opened. It may be corrupted or renamed."
PDF_IS_PASSWORD_PROTECTED = "This PDF is password-protected. Please remove the password and upload again."
PDF_HAS_NO_TEXT = "No readable text was found. The PDF is probably a scanned image."
TXT_IS_BLANK = "The text file is blank. There is nothing to read."
CSV_CANNOT_BE_READ = "The CSV file could not be read. Please check its format."
CSV_HAS_NO_ROWS = "The CSV file has column names but no data rows."
EXCEL_CANNOT_BE_OPENED = "This Excel file could not be opened. It may be corrupted or renamed."
EXCEL_SHEETS_ARE_EMPTY = "All sheets in this Excel file are empty."


# ---- Agent ----
AGENT_NO_CLEAR_ANSWER = "I couldn't find a clear answer in the BIODNA documents."



# ---- Input guardrails ----
QUESTION_IS_EMPTY = "Please type a question."
QUESTION_TOO_SHORT = "Your question is too short. Please ask a full question."
QUESTION_TOO_LONG = f"Your question is too long. Please keep it under {config.MAX_QUESTION_LENGTH} characters."
QUESTION_HAS_NO_WORDS = "Your question doesn't contain any words. Please ask a question about the lab."
PROMPT_INJECTION_BLOCKED = "This question tries to change BIODNA's rules, so it can't be answered."
DIAGNOSIS_BLOCKED = ("BIODNA can't diagnose, interpret patient results or suggest treatment. "
                     "Please consult the treating doctor or the consultant pathologist.")
PERSONAL_DATA_BLOCKED = ("Please don't enter patient personal details such as phone numbers, "
                         "Aadhaar numbers or email addresses. Ask your question without them.")




# ---- Output guardrails ----
NOT_FOUND_IN_DOCUMENTS = "I couldn't find this in the BIODNA documents."
ANSWER_NOT_FROM_DOCUMENTS = ("This answer was not checked against the BIODNA documents. "
                             "Please verify it before use.")



# ---- LLM errors ----
LLM_NO_INTERNET = "BIODNA can't reach the AI service. Please check your internet connection and try again."
LLM_INVALID_TOKEN = ("The Hugging Face token is missing, wrong, or lacks permission. Check HF_TOKEN in the .env "
                     "file, and make sure the token allows 'Make calls to Inference Providers'.")
LLM_CREDITS_USED_UP = "The free Hugging Face credit for this month is used up. Please try again later or check your Hugging Face billing page."
LLM_TOO_MANY_REQUESTS = "The AI service is busy right now. Please wait a moment and ask again."
LLM_MODEL_UNAVAILABLE = "The AI model in HF_MODEL is not available. Check the model name in the .env file."
LLM_UNKNOWN_ERROR = "Something went wrong while answering. Please try again."

# ---- App (user interface) ----
APP_STARTING = "Starting BIODNA: connecting to the AI services and opening the document database..."
APP_SIDEBAR_LOADING = "Loading documents..."
APP_ANSWER_VALIDATED = "✓ Checked against the sources by the Answer Validator"
APP_NO_DOCUMENTS = "No documents are loaded yet. Upload files or click 'Load sample documents' in the sidebar."
APP_NO_FILES_CHOSEN = "Please choose one or more files first."
APP_UNEXPECTED_UPLOAD_ERROR = "This file could not be added because of an unexpected error. Please try another file."
APP_DISCLAIMER = ("For BIODNA lab staff reference only. Always verify against the current SOP. "
                  "BIODNA does not diagnose or advise on treatment.")

# ---- Answer Validator ----
ANSWER_NOT_SUPPORTED = "The Answer Validator could not confirm this answer from the sources: {reason} Please check the sources below."
ANSWER_COULD_NOT_BE_VALIDATED = "This answer could not be double-checked by the Answer Validator. Please verify it against the sources."
