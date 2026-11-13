# Unpack bundle-*.bin from ~/Downloads into assets/real/<name>.png
# A name inside a bundle may only land inside assets/real: an absolute path, or one that climbs out with ../, is skipped.
import sys,struct,os,glob
out=os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'assets','real'))
for f in (sys.argv[1:] or sorted(glob.glob(os.path.expanduser('~/Downloads/bundle-*.bin')))):
    b=open(f,'rb').read(); i=0; n=0; bad=0
    while i<len(b):
        L=struct.unpack('>I',b[i:i+4])[0]; name=b[i+4:i+4+L].decode(); i+=4+L
        D=struct.unpack('>I',b[i:i+4])[0]; d=b[i+4:i+4+D]; i+=4+D
        p=os.path.realpath(os.path.join(out,name if os.path.splitext(name)[1] else name+'.png'))
        if not p.startswith(out+os.sep): bad+=1; continue
        os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(d); n+=1
    print(os.path.basename(f),n,'frames'+(f', {bad} skipped (names that point outside assets/real)' if bad else '')); os.remove(f)
