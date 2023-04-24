import os
from lmql.runtime.stats import Stats

def is_available():
    if "LMQL_BROWSER" in os.environ:
        # sadly not for now (need to investigate wasm port)
        return False
    return True

def unicode(v):
    r = v.decode("utf-8", "ignore")
    assert type(r) is str
    return r
class TiktokenTokenizer:
    def __init__(self, model_identifier):
        import tiktoken

        self.model_identifier = model_identifier
        self.enc = tiktoken.encoding_for_model(model_identifier)
        self.vocab = {unicode(v): i for i,v in enumerate(self.enc.token_byte_values())}

        self.stats = Stats("tiktoken")

        for i in range(self.enc.n_vocab, self.enc.max_token_value):
            token_name = f"<|special_{i}|>"
            assert token_name not in self.vocab, f"token {token_name} already in vocab"
            self.vocab[token_name] = i

    # do not picke self.enc
    def __getstate__(self):
        return {
            "model_identifier": self.model_identifier,
            "vocab": self.vocab
        }
    
    def __setstate__(self, state):
        import tiktoken
        
        self.model_identifier = state["model_identifier"]
        self.vocab = state["vocab"]
        self.enc = tiktoken.encoding_for_model(self.model_identifier)
        self.stats = Stats("tiktoken")

    def encode(self, text):
        return self.enc.encode(text, allowed_special={"<|endoftext|>"})

    def tokenize(self, text):
        return [self.enc.decode([i]) for i in self.enc.encode(text)]

    def decode(self, ids):
        return self.enc.decode(ids)

    def __call__(self, text_or_list):
        if isinstance(text_or_list, str):
            input_ids = self.encode(text_or_list)
        else:
            input_ids = [self.encode(text) for text in text_or_list]

        return {
            "input_ids": input_ids,
        }

    @property
    def vocab_size(self):
        return self.enc.max_token_value + 1
    
    @property
    def eos_token_id(self):
        return self.enc.eot_token

    @property
    def bos_token_id(self):
        return self.enc.eot_token

    def convert_tokens_to_string(self, tokens):
        return "".join(tokens)

    @property
    def name(self):
        return "tiktoken_cl100k_base"

def get_tokenizer(model_identifier):
    import tiktoken

    if model_identifier.startswith("openai/"):
        model_identifier = model_identifier[len("openai/"):]
    
    return TiktokenTokenizer(model_identifier)