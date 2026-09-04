from pydantic import HttpUrl


GITHUB_REPO_URL_MESSAGE = "repo_url must be an HTTPS GitHub repository URL: https://github.com/{owner}/{repo}"


def validate_public_github_repo_url(value: HttpUrl) -> HttpUrl:
    path_segments = [segment for segment in value.path.split("/") if segment]
    has_default_port = value.port in (None, 443)
    has_exact_repo_path = len(path_segments) == 2 and value.path == f"/{path_segments[0]}/{path_segments[1]}"
    if (
        value.scheme != "https"
        or value.host != "github.com"
        or value.username is not None
        or value.password is not None
        or not has_default_port
        or value.query is not None
        or value.fragment is not None
        or not has_exact_repo_path
    ):
        raise ValueError(GITHUB_REPO_URL_MESSAGE)
    return value


def canonical_github_repo_url(value: HttpUrl) -> str:
    validate_public_github_repo_url(value)
    owner, repo = [segment for segment in value.path.split("/") if segment]
    return f"https://github.com/{owner}/{repo}"
