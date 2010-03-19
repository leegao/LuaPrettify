#!/usr/bin/python
# This Python file uses the following encoding: utf-8
import re

def NewLineBlocks(src):
    block_keywords_start = [
        re.compile(r".*?function.*?\(.*\)"),
        re.compile(r"if (.|[()\[\]])+ then"),
        re.compile(r".+ do"),
        re.compile(r"repeat"),
    ]
    block_keywords_intermediate = [
        re.compile(r"elseif .+ then"),
        re.compile(r"else\s*(?=\n)"),
    ]
    block_keywords_end = [
        re.compile(r"\s*end\s*"),
        re.compile(r"until .+"),
    ]
    for token in block_keywords_start+block_keywords_intermediate:
        src = token.sub(lambda g: g.group()+"\n", src)
    for token in block_keywords_end:
        src = token.sub(continuous(src), src)
    return src

def continuous(src):
    def temp_(g):
        ws = re.compile("((.|[ \t])+)?(?=end|until)")
        mt =  ws.match(src[g.end():])
        return "\n"+g.group().strip()+("\n" if not ("end" not in mt.group() if mt else None) else " ")
    return temp_

REPLACEMENT_CACHE = {}
def push_cache(obj):
    key = "$$K"+str(len(REPLACEMENT_CACHE.keys()))+"$$"
    REPLACEMENT_CACHE[key] = obj
    return key
def get_cache(key):
    return REPLACEMENT_CACHE[key]

def ReplaceCommentsAndStrings(src):
    comment_multi = re.compile(r"\-\-\[\[(.|\s)*?\]\]", re.MULTILINE) # --[[ ]]
    comment_single = re.compile(r"\-\-.*") # --
    string_sq = re.compile(r"\'.*?\'") # ''
    string_dq = re.compile(r'\".*?\"') # ""
    string_multi = re.compile(r"\[\[(.|\s)*?\]\]", re.MULTILINE) # [[ ]]
    repl = [comment_multi,comment_single,string_sq,string_dq,string_multi]
    for pat in repl:
        src = pat.sub(lambda g: push_cache(g.group()), src)
    return src

def BreakSemi(src):
    semi = re.compile(r"\;+")
    src = semi.sub("\n", src.replace("\n",";"))
    return src

def SrcFormat(src):
    block_keywords_start = [
        re.compile(r".*?function.*?\(.*\)"),
        re.compile(r"if .+ then"),
        re.compile(r".+ do"),
        re.compile(r"repeat"),
    ]
    block_keywords_intermediate = [
        re.compile(r"elseif .+ then"),
        re.compile(r"else\s*(?=\n)"),
    ]
    block_keywords_end = [
        re.compile(r"end"),
        re.compile(r"until .+"),
    ]
    level = 0
    lines = src.split("\n")
    lines__ = []
    for line in lines:
        processed = False
        for st in block_keywords_start:
            if st.match(line):
                processed = True
                lines__+= [level*"\t"+line]
                level+=1
                if level < 0: level = 0
        for inter in block_keywords_intermediate:
            if inter.match(line):
                processed = True
                lines__+= [ (level-1)*"\t"+line ]
                if level < 0: level = 0
        for end in block_keywords_end:
            if end.match(line):
                processed = True
                level -= 1
                lines__+= [ (level)*"\t" + line]
                if level < 0: level = 0
        if not processed:
            lines__+= [ level*"\t" + line]
    src = "\n".join(lines__)
    return src

def PrettyLua(src):
    #Step 1: Replace comments and strings
    src = ReplaceCommentsAndStrings(src)
    #Step 2: Break at ;'s
    src = BreakSemi(src)
    #Step 3: Blocks are on same lines
    src = NewLineBlocks(src.strip())
    src = "\n".join([st.strip() for st in src.split("\n")])
    src =re.compile(r"\n\s*?\n").sub("\n",src)
    #Step 4: Begin Src formatting
    src = SrcFormat(src)
    #Step 5: Reverse Literal Replacements
    repl = re.compile(r"\$\$K.+?\$\$")
    while repl.search(src):
        src = repl.sub(lambda g: REPLACEMENT_CACHE[g.group()], src)
    return src.strip()

def tidy(*filenames):
    for filename in filenames:
        print "-- @@"+filename+"@@ --"
        _f = open(filename, "r")
        data = _f.read()
        _f.close()
        print PrettyLua(data), "\n\n"

prettify = PrettyLua        

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: tidy.py <filename.lua> [<filename2.lua> ...]"
        sys.exit(1)
    tidy(*sys.argv[1:])