# analysis/__init__.py
import pkgutil, importlib

QUESTION_REGISTRY = {}

def _register(qid):
    def decorator(fn):
        QUESTION_REGISTRY[qid] = fn
        return fn
    return decorator

# Auto-import every .py in this package so each can self-register
for m in pkgutil.iter_modules(__path__, __name__ + "."):
    importlib.import_module(m.name)

def run_analysis_for_question(df, mapping, question, domain, **kw):
    qid = question["id"]
    fn = QUESTION_REGISTRY.get(qid)
    if not fn:
        from .custom import custom_question
        return custom_question(df, question, domain)
    return fn(df, **kw)
