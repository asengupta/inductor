edge(a,b).
edge(b,c).
edge(c,d).
edge(p,q).

instr(0,mov,ax,bx,1).
instr(1,jmp,ax,dummy,2).
instr(2,jmp,ax,dummy,2).

has(proc1,[0,1]).
has(proc2,[2]).

belongs_to_proc(PROC,instr(ID,_,_,_,_),YESNO) :- (has(PROC,INSTRS), belongs_to(PROC,instr(ID,_,_,_,_),INSTRS,BELONGS_TO), YESNO = BELONGS_TO).
belongs_to_proc(PROC,instr(_,_,_,_,_),YESNO) :- \+ has(PROC,_),YESNO = 'NO'.
belongs_to(_,instr(_,_,_,_,_),[],YESNO) :- YESNO = 'NO'.
belongs_to(PROC,instr(ID,_,_,_,_),[H_ID|T_IDS],YESNO) :- (H_ID =:= ID,YESNO = 'YES');
                                                         (belongs_to(PROC,instr(ID,_,_,_,_),T_IDS,CHILD_RESULT),YESNO = CHILD_RESULT).

affects(X) :- instr(_,mov,X,_,_).

jmps([],0).
jmps([instr(_,jmp,_,_,_) | R],SUM) :- jmps(R, NEWSUM), SUM is NEWSUM+1, write("Added one...").
jmps([instr(_,_,_,_,_) | R],SUM) :- jmps(R, SUM).
idjmps([],0).
idjmps([X|R],SUM) :- number(X),instr(X,jmp,_,_,_),idjmps(R,NEWSUM),SUM is NEWSUM+1.
idjmps([X|R],SUM) :- number(X),instr(X,_,_,_,_),idjmps(R,NEWSUM),SUM is NEWSUM.

immediately_before(ID1,ID2) :- instr(ID1,_,_,_,T1),instr(ID2,_,_,_,T2), write('Checking for immediately before...'), T1 =:= T2 - 1.
path(X,Y) :- edge(X,Y).
path(X,Y) :- edge(X,Z),path(Z,Y).

path(a,b).
