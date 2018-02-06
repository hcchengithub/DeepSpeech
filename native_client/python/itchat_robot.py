
# This program is from :
# %USERPROFILE%\Documents\GitHub\ailab_RockPaperScissors\itchat_robot.py 
# The main program of the "剪刀、石頭、布" project 
# Now modified for Mozilla DeepSpeech demo with itchat remote control 

import sys,os,time,random
from timeit import default_timer as timer
from deepspeech.model import Model  # the Mozilla DeepSpeech model 
# import numpy as np
# import matplotlib.pyplot as plt
# import tensorflow as tf
# import scripts.label_image2 as ai  # Google Inception model 

from itchat.content import * # TEXT PICTURE 等 constant 的定義
import itchat
import peforth
# ------------ Mozilla DeepSpeech ----------------------------------
import scipy.io.wavfile as wav  # read .wav file for DeepSpeech
# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.75

# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
WORD_COUNT_WEIGHT = 1.00

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 1.00

# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9

# deepspeech models/output_graph.pb native_client/audio/2830-3980-0043.wav models/alphabet.txt models/lm.binary models/trie
def recognize(
        model="../models/output_graph.pb",
        audio="../audio/2830-3980-0043.wav",
        alphabet="../models/alphabet.txt",
        lm="../models/lm.binary",
        trie="../models/trie"):
    print('Loading model from file %s' % (model), file=sys.stderr)
    model_load_start = timer()
    ds = Model(model, N_FEATURES, N_CONTEXT, alphabet, BEAM_WIDTH)
    model_load_end = timer() - model_load_start
    print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)

    if lm and trie:
        print('Loading language model from files %s %s' % (lm, trie), file=sys.stderr)
        lm_load_start = timer()
        ds.enableDecoderWithLM(alphabet, lm, trie, LM_WEIGHT,
                               WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)
        lm_load_end = timer() - lm_load_start
        print('Loaded language model in %0.3fs.' % (lm_load_end), file=sys.stderr)

    fs, audio = wav.read(audio)
    # We can assume 16kHz
    audio_length = len(audio) * ( 1 / 16000)
    assert fs == 16000, "Only 16000Hz input WAV files are supported for now!"

    print('Running inference.', file=sys.stderr)
    inference_start = timer()
    result = ds.stt(audio, fs)
    print(result, file=sys.stderr)
    inference_end = timer() - inference_start
    print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, audio_length), file=sys.stderr)
    return result 
# ------------ Mozilla DeepSpeech ----------------------------------

# WeChat chatroom name 
chatroom = "AILAB" # "剪刀、石頭、布"

# PIC list, who can still remote control the robot PC when chatroom nickName is 
# not match. 負責管理的人員名單 Robot 所在的任何 chatroom 只要被 @PIC 就會當作
# command line 拿去處理。
PIC = ("hcchen5600",)
    # 這裡很好玩,上面這個逗點如果漏掉, PIC 就變成是個 str 結果連 hc 也算！那就錯了。
    # 增加 陳厚成0922 進 PIC 名單的方法: 
    # __main__ :: PIC=("hcchen5600","陳厚成0922")
    
# Anti-Robot delay time , thanks to Rainy's great idea.
nextDelay = 1
def nextDelay_msg():
    global nextDelay 
    nextDelay = random.choice((2,3,3,4,4,4,5,5,5,5,6,6,6,7,7,8,9,10,11,12,13,14,15)) 
    return 'Next anti-robot delay time: %i seconds\n' % (nextDelay)

# Initialize debugger peforth 
peforth.ok(loc=locals(),glo=globals(),cmd='''
    cr value main // ( -- {loc,glo,prompt} ) main program variables
    main :> [0] value main.locals // ( -- dict ) main locals
    : (sh) ( "command line" -- errorlevel ) // Bash shell command line
        __main__ :> os.system(pop()) ; 
    : sh ( <command line> -- errorlevel ) // Bash shell command line
        CR word (sh) ;
    \ Check ffmpeg, ffprobe, and the needed '~/GitHub/DeepSpeech/native_client/audio' directory
        sh ffmpeg -version
        [if] cr ." Fatal error! ffmpeg not found which is used to convert pictures." cr bye [then]
        sh ffprobe -version
        [if] cr ." Fatal error! ffprobe not found which is for pictures' duration." cr bye [then]
        \ 預設在 /home/hcchen5600/GitHub/DeepSpeech/native_client/python 執行，檢查 audio/ and models/ 存不存在
        s" ls ../audio" (sh)
        [if] cr ." Fatal error! '~/GitHub/DeepSpeech/native_client/audio' directory not found." cr bye [then]
        s" ls ../models" (sh)
        [if] cr ." Fatal error! '~/GitHub/DeepSpeech/native_client/models' directory not found." cr bye [then]
        
    \ define variables
        __main__ :> time constant time // ( -- module )
        none value locals // ( -- dict ) at each breakpoint
        none value globals // ( -- dict ) at each breakpoint
        none value msg // ( -- obj ) itchat dynamic msg package 
    \ redefine the 'bye' command to logout itchat first
        : bye main.locals :> ['itchat'].logout() bye ; 
    \ exit \ Don't forget this!!
    ''')  
    
# Sending message to friend or chatroom depends on the given 'send'
# function. It can be itchat.send or msg.user.send up to the caller.
# WeChat text message has a limit at about 2000 utf-8 characters so
# we need to split a bigger string into chunks.
def send_chunk(text, send, pcs=2000):
    s = text
    while True:
        if len(s)>pcs:
            time.sleep(random.choice((3,4,4,5,5,5,5,6,6,6,7,7,8,9,10)))  # Anti-Robot delay 
            print(s[:pcs]); 
            send(s[:pcs])
        else:
            # normal case already delaied before calling send_chunk()
            print(s); 
            send(s)
            break
        s = s[pcs:]    

# Console is a peforth robot that listens and talks.
# Used in chatting with both friends and chatrooms.
def console(msg,cmd):
    if cmd:
        print(cmd)  # already on the remote side, don't need to echo. 
        peforth.vm.push(msg); peforth.vm.dictate("to msg")  # Availablize msg in peforth interpreter
        if peforth.vm.debug==11: peforth.ok('11> ',loc=locals(),cmd=":> [0] to locals cr")  # breakpoint
        # re-direct the display to peforth screen-buffer
        peforth.vm.dictate("display-off")  
        try:
            peforth.vm.push((locals(),globals(),'console prompt'))
            peforth.vm.dictate(":> [0] to locals " + cmd)
        except Exception as err:
            errmsg = "Failed! : {}".format(err)
            peforth.vm.dictate("display-on")
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(errmsg + nextDelay_msg() + "\nOK", msg.user.send)
        else:
            # Normal cases 
            peforth.vm.dictate("display-on screen-buffer")
            screen = peforth.vm.pop()[0]
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk(screen + nextDelay_msg() + "\nOK", msg.user.send)

#        
# 讓 Inception V3 Transfered Learning 看照片，回答 剪刀、石頭、布
#        
def predict(msg):
    if peforth.vm.debug==22: peforth.ok('22> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    results = time.ctime() + '\n'
    results += 'Google Inception V3 Transfered Learning thinks it is:\n'
    pathname = 'download/' + msg.fileName # 照片放在 working directory/download 下
    msg.download(pathname)  
    # TensorFlow 的 tf.image.decode_bmp/jpen/png/pcm 很差，改用 ffmpeg 
    peforth.vm.dictate("sh ffmpeg -i {} -y 1.png".format(pathname)+"\ndrop\n")  
    # results += ai.predict("1.png")
    peforth.vm.dictate("sh rm {}".format(pathname)+"\ndrop\n")
    time.sleep(nextDelay)  # Anti-Robot delay 
    send_chunk(results + nextDelay_msg(), msg.user.send)

@itchat.msg_register((ATTACHMENT,VIDEO,VOICE), isGroupChat=True)
def attachment(msg):
    if peforth.vm.debug==33: peforth.ok('33> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        pathname = 'download/' + msg.fileName
        msg.download(pathname)
        if msg.fileName.lower().endswith(('.mp3','.3gpp','.aac','.wav','.wma','.pcm')):
            peforth.vm.dictate("sh ffmpeg -i '{0}' -ar 16000 -ab 256k -ac 1 '{0}'.wav".format(pathname)+"\ndrop\n")  
            result = recognize(audio=pathname+".wav")
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk('Mozilla DeepSpeech heard you said: %s \nreceived at %s\n' % (result,time.ctime()) + nextDelay_msg(), msg.user.send)
        else:
            time.sleep(nextDelay)  # Anti-Robot delay 
            send_chunk('Attachment: %s \nreceived at %s\n' % (msg.fileName,time.ctime()) + nextDelay_msg(), msg.user.send)

@itchat.msg_register(TEXT, isGroupChat=True)
def chat(msg):
    def myConsole(msg):
        # 本 chat 當作 peforth 命令處理
        cmd = msg.text + '\n' # 保證可以 split() 
        cmd = cmd.split("\n",maxsplit=1)[1] # remove the first line: @nickName ...
        console(msg, cmd)                   # 避免帶有空格的 nickName 惹問題
    def chat(msg):
        # 處裡本 chat, @版主 時當 peforth 命令處理否則只是在 robot PC 上顯示
        if msg.isAt: 
            myConsole(msg)
        else:    
            # Shown on the robot computer
            print(time.ctime(msg.CreateTime), end=" ")
            for i in msg.User['MemberList']:
                if i.UserName == msg.ActualUserName:
                    print(i.NickName)
            print(msg.text)
    if peforth.vm.debug==44: peforth.ok('44> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        chat(msg)
    else:
        # 開個後門，否則 Chatroom nickName 改了就控制不到。
        # 當 Chatroom nickName 只有部分符合時，並且只針對 PIC 的發言處理。
        # 非 @版主 也在 Robot PC 上顯示出來是為了確認 Robot 有反應。
        if msg.user.NickName.find(chatroom) != -1:
            for i in msg.User['MemberList']:
                if peforth.vm.debug==44: peforth.ok('44a> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
                if (i.UserName == msg.ActualUserName) and (i.NickName in PIC):
                    chat(msg)
                    
@itchat.msg_register(PICTURE, isGroupChat=True)
def picture(msg):
    if peforth.vm.debug==55: peforth.ok('55> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        # predict(msg) 玩 DeepSpeech 暫時關閉
        pass

@itchat.msg_register(RECORDING, isGroupChat=True)
def recording(msg):
    if peforth.vm.debug==77: peforth.ok('77> ',loc=locals(),cmd=":> [0] to locals locals :> ['msg'] to msg cr")  # breakpoint
    if msg.user.NickName==chatroom: # 只在特定的 chatroom 工作，過濾掉其他的。
        pathname = 'download/' + msg.fileName
        msg.download(pathname)
        peforth.vm.dictate("sh ffmpeg -i {0} -ar 16000 -ab 256k -ac 1 {0}.wav".format(pathname)+"\ndrop\n")  
        result = recognize(audio=pathname+".wav")
        time.sleep(nextDelay)  # Anti-Robot delay 
        send_chunk('Mozilla DeepSpeech heard you said: %s \nreceived at %s\n' % (result,time.ctime()) + nextDelay_msg(), msg.user.send)
        
# peforth.vm.debug = 44
if peforth.vm.debug==66: peforth.ok('66> ',loc=locals(),cmd=":> [0] to locals cr")  # breakpoint    
itchat.auto_login(enableCmdQR=2, hotReload=False)
itchat.run(debug=True, blockThread=True)
peforth.ok('Examine> ',loc=locals(),cmd=':> [0] to main.locals cr time :> ctime() . cr')

'''

# --------------- Playground ---------------------------------------------------
\ Ynote: "Itchat Robot Toolkit 在這兒集中管理"
\ Setup the playground for testing without itchat (avoid the need to login)
\ 弄出個 msg 來供 function test 測試以及 debug 用，而無須 itchat 連線。

    <accept>
    <py>
    def msg():
        pass
    def _():
        pass
    msg.user = _    
    msg.CreateTime = 1504452397.47364
    msg.user.send = str # 吃掉 argument 
    msg.user.NickName = 'AILAB'    
    msg.isAt = True
    def _():
        print('msg.user.verify() ... pass')
    msg.user.verify = _
    msg.fileName = 'test.jpg'
    msg.type = 'fil' # also 'img'(image), 'vid'(video)
    def _(fileName):
        print('Downloaded %s from WeChat cloud' % fileName)
    msg.download = _
    msg.text = "Message text from the WeChat cloud"
    msg.Text = msg.text
    msg.User = {}
    msg.User['MemberList'] = []
    # user believer
    msg.ActualUserName = "dynamic-id1122aabb"
    def _():
        pass
    _.UserName = msg.ActualUserName
    _.NickName = "believer"
    msg.User['MemberList'].append(_)
    # user hcchen5600
    msg.ActualUserName = "mememe-hcchen5600"
    def _():
        pass
    _.UserName = msg.ActualUserName
    _.NickName = "hcchen5600"
    msg.User['MemberList'].append(_)
    push(msg)
    </py> to msg
    msg __main__ :: peforth.projectk.msg=pop(1)
    \ Introduce peforth value msg to peforth global 
    </accept> dictate

    \ 應用例
    
    __main__ :> predict(msg) . cr
    __main__ :> console(msg,".s")
    __main__ :> attachment(msg)
    __main__ :> picture(msg)
    msg :: text="@版主\nwords" __main__ :> chat(msg)
    \ 把下面的遠端來灌程式, e.g. check getfile 等整個弄成 ss 
    ss msg :: text="@版主\n"+pop(1) __main__ :> chat(msg)
    msg :: text="@版主\ncheck" __main__ :> chat(msg)

    
    \ 瞭解這個虛擬的 msg 
    \ See also: "itchat msg 解析.note"
    
    Examine> msg . cr
    <function compyle_anonymous.<locals>.msg at 0x0000020FADBAF400>
    
    Examine> msg (see)
    {
        "__class__": "function",
        "__module__": "peforth.projectk",
        "__doc__": null,
        "user": {
            "__class__": "function",
            "__module__": "peforth.projectk",
            "__doc__": null,
            "send": {
                "__class__": "builtin_function_or_method",
                "__module__": "builtins",
                "__doc__": "print(value, ..., sep=' ', end='\\n', file=sys.stdout, flush=False)\n\nPrints the values to a stream, or to sys.stdout by default.\nOptional keyword arguments:\nfile:  a file-like object (stream); defaults to the current sys.stdout.\nsep:   string inserted between values, default a space.\nend:   string appended after the last value, default a newline.\nflush: whether to forcibly flush the stream."
            },
            "NickName": "A believer",
            "verify": {
                "__class__": "function",
                "__module__": "peforth.projectk",
                "__doc__": null
            }
        },
        "isAt": true,
        "fileName": "20171222153010.jpg",
        "type": "fil",
        "download": {
            "__class__": "function",
            "__module__": "peforth.projectk",
            "__doc__": null
        },
        "text": "Message text from the WeChat cloud",
        "Text": "Message text from the WeChat cloud"
    }

\ itchat robot toolkit 由遠端灌過來給 robot 執行的程式集
\ Ynote: Itchat Robot Toolkit 在這兒集中管理

    \ 一開始設定先報時
    cr time :> ctime() . cr \ print recent time on Robot PC when making this setting
    
    \ 到了 runtime 憑 msg.user.NickName 才知道 active chatroom 是那個，因此 msg
    \ 動態地要用到。主程式裡要提供以下變數：
    \   none value msg
    \ 進 console() 以及 breakpoints 要填好 msg
    \   peforth.vm.push(msg); 
    \   peforth.vm.dictate("to msg")  # Availablize msg in peforth interpreter

    \ 主程式的設定與變數參考下來
    __main__ :> chatroom constant chatroom // ( -- text ) The working chatroom NickName
    : nextDelay __main__ :> nextDelay ; // ( -- int ) Anti-robot delay time before every send()
    
    \ get itchat module object
    py> sys.modules['itchat'] constant itchat // ( -- module ) WeChat automation
    
    \ get PIL graph tool
    import PIL.ImageGrab constant im // ( -- module ) PIL.ImageGrab

    \ 複習每個東西
    \ __main__ :> chatroom \ 主程式指定要 focus 的 chatroom nickName
    \ msg :> user \ 本 active chatroom 的 object 
    \ msg.user.NickName # chatroom name
    \ 當前發言者的 NickName 要用以下三個東西輾轉找出來
    \   msg.ActualUserName # the 發言者的 dynamic ID
    \   msg.User['MemberList'][i].UserName # a member's dynamic ID
    \   msg.User['MemberList'][i].NickName # a member's nickname
    \ itchat :> search_chatrooms(pop()) constant chatrooms  \ 全部 chatrooms 這沒什麼意義
    \ itchat :> search_chatrooms(pop())[0].nickName \ 這沒什麼意義
    \ chatrooms count ?dup [if] dup [for] \ 這也沒什麼意義
    \     dup t@ - ( COUNT i ) . space ( COUNT ) 
    \ [next] drop [then]

    \ 以下自訂命令要遵守的規則
    \ a) 必須合併所有的 message 做一次 send()
    \ b) 這個唯一的 send() 之前必須自己做 anti-robot delay 
    \ c) console() 最終會重算 nextDelay time 且印出去，這裡不必做。
    
    : check // ( -- ) Get robot pc desktop screenshot
        cr time :> ctime() . cr \ print the recent time on the robot pc
        im :: grab().save("1.jpg") \ capture screenshot 
        nextDelay time :: sleep(pop()) \ anti-robot delay before every send()
        msg :> user.send("@img@1.jpg") \ send to chatroom 
        . cr ; \ shows the responsed message

    : getfile // ( "pathname" -- ) Get source code for debugging
        py> str(pop()).strip() \ trim pathname 
        s" @fil@" swap + \ command string 
        cr time :> ctime() . space s" getfile: " . dup . cr
        nextDelay time :: sleep(pop()) \ anti-robot delay before every send()
        msg :> user.send(pop()) \ send to chatroom so everybody gets it
        . cr ; \ shows the responsed message
        /// In case source code were modified on the robot pc.
        
[x] chatroom nickName 改過何時生效?
    private AILAB --> AILAB 結果 --> 過幾秒之後生效，不是馬上也差不多了。
    
'''
