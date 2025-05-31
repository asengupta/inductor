edge(a,b).
edge(b,c).
edge(c,d).
edge(p,q).

instr(0,mov,ax,bx,1).
instr(1,jmp,ax,dummy,2).

affects(X) :- instr(_,mov,X,_,_).

jmps([],0).
jmps([instr(_,jmp,_,_,_) | R],SUM) :- jmps(R, NEWSUM), SUM is NEWSUM+1, write("Added one...").
jmps([instr(_,_,_,_,_) | R],SUM) :- jmps(R, SUM).

immediately_before(ID1,ID2) :- instr(ID1,_,_,_,T1),instr(ID2,_,_,_,T2), write('Checking for immediately before...'), T1 =:= T2 - 1.
path(X,Y) :- edge(X,Y).
path(X,Y) :- edge(X,Z),path(Z,Y).

path(a,b).
