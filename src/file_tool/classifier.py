RESUME_KEYWORDS = {
    "resume", "interview", "job", "career", "linkedin", "offer",
    "application", "tesla-mfg-test-eng", "mach", "nvidia"
}

ENGINEERING_KEYWORDS = {
    "engineering", "python", "stm32", "github", "backend",
    "automation", "project", "vault", "code", "api", "worklog", "vp mach",
}

PERSONAL_KEYWORDS = {
    "taxes", "pay stubs", "medical", "psych", "verizon", "iphone",
    "groceries", "membership", "ticket", "ynab", "net worth", "bills"
}

ARCHIVE_KEYWORDS = {
    "archive", "old", "backup"
}

INBOX_KEYWORDS = {
    "inbox", "imports", "new folder", "untitled"
}


def contains_any_keywords(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_name(name: str) -> str:
    lowered = name.lower()

    if contains_any_keywords(lowered, ARCHIVE_KEYWORDS):
        return "ARCHIVE"

    if contains_any_keywords(lowered, INBOX_KEYWORDS):
        return "INBOX"

    if contains_any_keywords(lowered, RESUME_KEYWORDS):
        return "RESUME"

    if contains_any_keywords(lowered, ENGINEERING_KEYWORDS):
        return "ENGINEERING"

    if contains_any_keywords(lowered, PERSONAL_KEYWORDS):
        return "PERSONAL"

    return "INBOX"


if __name__ == "__main__":
    test1 = contains_any_keywords("archive", {"old"})
    print("test1:", test1)

    test2 = contains_any_keywords("archive", {"archive"})
    print("test2:", test2)

    test3 = contains_any_keywords("archive_9-19-25", ARCHIVE_KEYWORDS)
    print("test3:", test3)

    print(classify_name("ARCHIVE_9-19-25"))
    print(classify_name("Linkedin Resumes 3-23-26"))
    print(classify_name("Stm32"))
    print(classify_name("Verizon bills"))
    print(classify_name("New folder"))