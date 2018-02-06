
print("用 ipython copy-paste 下列 snippet 即可把這些檔案全都改好 format")
print("用 ipython copy-paste 下列 snippet 即可對整批 .wav 檔做 deepspeech 辨識")
exit()

import os
names = [
    "and security.wav",
    "and security2.wav",
    "and think i live within.wav",
    "God is my refuge.wav",
    "i will behold myself.wav",
    "i will identify.wav",
    "my strength.wav",
    "the citadel.wav",
    "where i am safe and can not be attached.wav",
    "where i persceive.wav",
    "with what i think is refuge.wav"
    ]

# 把這些檔案全都改好 format
for i in names:
    os.system('ffmpeg -i "{0}" -ar 16000 -ab 256k -ac 1 "{0}"'.format(i))

# -------- test all of them -------------------
# 對整批 .wav 檔做 deepspeech 辨識
for i in names:
    os.system('deepspeech models/output_graph.pb audio/"{}" models/alphabet.txt models/lm.binary models/trie'.format(i))
    
'''
    執行結果
    
    "and security.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.740s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.193s.
    Running inference.
    and his security
    Inference took 9.067s for 1.802s audio file.

    "and security2.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.612s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.201s.
    Running inference.
    and security
    Inference took 5.041s for 1.267s audio file.

    "and think i live within.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.609s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.164s.
    Running inference.
    and think i leave to be in
    Inference took 9.726s for 2.328s audio file.

    "God is my refuge.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.600s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.203s.
    Running inference.
    god is my red fit
    Inference took 7.017s for 2.319s audio file.

    "i will behold myself.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.600s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.149s.
    Running inference.
    i will be hole to myself
    Inference took 8.890s for 2.311s audio file.

    "i will identify.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.607s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.221s.
    Running inference.
    how well i gantisig
    Inference took 7.086s for 1.923s audio file.

    "my strength.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.606s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.187s.
    Running inference.
    my strength
    Inference took 4.237s for 1.302s audio file.

    "the citadel.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.597s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.159s.
    Running inference.
    he set a to
    Inference took 6.046s for 1.862s audio file.

    "where i am safe and can not be attached.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.589s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.153s.
    Running inference.
    where i am safe
    Inference took 7.394s for 2.389s audio file.

    "where i persceive.wav",
    Loading model from file models/output_graph.pb
    Loaded model in 0.592s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.154s.
    Running inference.
    well i perceive
    Inference took 5.764s for 1.828s audio file.

    "with what i think is refuge.wav"
    Loading model from file models/output_graph.pb
    Loaded model in 0.610s.
    Loading language model from files models/lm.binary models/trie
    Loaded language model in 1.151s.
    Running inference.
    with what i think is ree
    Inference took 5.718s for 2.389s audio file.

'''    