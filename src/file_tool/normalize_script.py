
def normalize_filename(filename):
    # Remove leading/trailing whitespace and replace multiple spaces with a single space
    normalized = ' '.join(filename.strip().split())
    # Replace spaces with underscores
    normalized = normalized.replace(' ', '_')
    # Convert to lowercase
    normalized = normalized.lower()
    return normalized


