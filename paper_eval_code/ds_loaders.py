
from datasets import load_dataset

def load_fineweb(lang_id: str, streaming: bool = False, limit: int | None = None):

    if streaming:
        ds = load_dataset(
            "HuggingFaceFW/fineweb-2",
            lang_id,
            split="train",
            streaming=True,
        )
        if limit:
            ds = ds.take(limit)

    else:
        split = f"train[:{limit}]" if limit else "train"
        ds = load_dataset(
            "HuggingFaceFW/fineweb-2",
            lang_id,
            split=split,
            streaming=False,
        )

    return ds

def load_rtr(idiom="rm-rumgr"):
    """Loads the RTR dataset for the specified idiom.
    Idiom should be one of 
    - "rm-rumgr"
    - "rm-sursilv"
    - "rm-sutsilv"
    - "rm-surmiran
    - "rm-puter"
    - "rm-vallader"
    """
    ds = load_dataset("ZurichNLP/rtr-transcripts", idiom)
    return ds["train"]

def load_babulins(idiom="rm-rumgr"):
    """The Babulins dataset is currently not openly available."""
    return None
