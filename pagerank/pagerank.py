import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transit_probs = dict()
    n = len(corpus)
    for filename in corpus:
        transit_probs[filename] = (1 - damping_factor) / n
    m = len(corpus[page])
    for filename in corpus[page]:
        transit_probs[filename] += damping_factor / m
    #if a page has no links, we can pretend it has links to all pages in the corpus, includingitself
    if m==0:
        transit_probs = {key: 1 / n for key in corpus}
    return transit_probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample_probs = {key: 0 for key in corpus}
    i = 0
    cur_page = random.sample(list(corpus.keys()), 1)[0]
    sample_probs[cur_page] += 1
    i += 1
    while i < n:
        transit_probs = transition_model(corpus, cur_page, damping_factor)
        cur_page = random.choices(list(transit_probs.keys()), weights=transit_probs.values(), k=1)[0]
        sample_probs[cur_page] += 1
        i += 1
    sample_probs = {key: (value / n) for key, value in sample_probs.items()}
    return sample_probs


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    cur_probs = {key: 1 / n for key in corpus.keys()}

    max_diff = 1
    iter = 0
    while max_diff > 0.001:
        iter += 1
        new_probs = {key: 0 for key in corpus.keys()}
        for key in corpus:
            new_probs[key] += (1 -  damping_factor) / n
            for key2 in corpus:
                if key in corpus[key2]:
                    new_probs[key] += damping_factor * cur_probs[key2] / len(corpus[key2])
                #if a page has no links,we can pretend it has links to
                #all pages in the corpus, including itself
                elif len(corpus[key2])==0:
                    new_probs[key] += damping_factor * cur_probs[key2] / n            
        # Normalise the new page ranks:
        norm_factor = sum(new_probs.values())
        new_probs = {key: (value / norm_factor) for key,value in new_probs.items()}
        max_diff = max(abs(cur_probs[key] - new_probs[key]) for key in corpus)
        cur_probs = new_probs
        
    return cur_probs
    

if __name__ == "__main__":
    main()
