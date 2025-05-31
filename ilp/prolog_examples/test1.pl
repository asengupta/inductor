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

append([],[],[]).
append([],[H|T],[H|T]).
append([H1|T1],L2,[H1|T3]) :- append(T1,L2,T3).

%append([a,b,c],[d,e,f],[H3|T3])
%=> append([b,c],[d,e,f],[HX|TX]) H3=a,T3=[HX|TX]
%=> append([c],[d,e,f],[HX|TX]) H3=b,T3=[HX|TX]
%=> append([],[d,e,f],[HX|TX]) H3=c,T3=[HX|TX]
%=> HX=d,TX=[e,f],H3=c,T3=[d,e,f]
%=> HX=c,TX=[d,e,f],H3=b,T3=[c,d,e,f]
%=> HX=b,TX=[c,d,e,f],H3=a,T3=[b,c,d,e,f]
%=> append([a,b,c],[d,e,f],[a|[b,c,d,e,f]])

reverse([],ACC,ACC).
reverse([H|T],ACC,R) :- reverse(T,[H|ACC],R).

%=> reverse([a|[b,c]],[],R) :- reverse([b,c],[a|[]],R)=reverse([b,c],[a],R)
%=> reverse([b|[c]],[a],R) :- reverse([c],[b|[a]],R) = reverse([c],[b,a],R)
%=> reverse([c|[]],[b,a],R) :- reverse([],[c|[b,a]],R) = reverse([],[c,b,a],R)
%=> reverse([],[c,b,a],R) :- reverse([],[c,b,a],[c,b,a])

len([],0).
len([_|T],L) :- len(T,X),L is X+1.

len2([],ACC,ACC).
len2([_|T],ACC,L) :- ACC1 is 1+ACC,len2(T,ACC1,L).

max2([],MAX,MAX).
max2([H|T],CURR_MAX,MAX) :- (H > CURR_MAX->NEWMAX=H;NEWMAX=CURR_MAX), max2(T,NEWMAX,MAX).

into2([],[]).
into2([H|T],RESULT) :- DBL is H*2, into2(T,RESULTX), RESULT=[DBL|RESULTX].

filter_even([],[]).
filter_even([H|T],R) :- filter_even(T,RESULTX), Remainder is H mod 2,(Remainder=:=0 -> R=[H|RESULTX];R=RESULTX).

double(X,Y) :- Y is X*2.
map2([],_,[]).
map2([H|T],Map_pred,[Mapped|RESULTX]) :- map2(T,Map_pred,RESULTX),call(Map_pred,H,Mapped).

isEven(X) :- 0 is X mod 2.
filter2([],_,[]).
filter2([H|T],FilterPred,[H|AlreadyFiltered]) :- call(FilterPred,H),filter2(T, FilterPred, AlreadyFiltered).
filter2([H|T],FilterPred,AlreadyFiltered) :- \+call(FilterPred,H),filter2(T, FilterPred, AlreadyFiltered).

%=> reverse([a|[b]],[X|[a]]) :- reverse([b],X)
%=> reverse([a|[b]],[X|[a]]) :- reverse([b],X)
%=> reverse([b],[X|[b]])
%=> reverse([b],[b])
%=> reverse([a|[b]],[H1=b|?])
