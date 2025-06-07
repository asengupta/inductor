member2(_,[]) :- false.
member2(-(K,V), [(-(KX,VX))|_]) :- K==KX,V==VX.
member2(-(K,V), [_|T]) :- member2(-(K,V),T).

get2(_,[],empty).
get2(K, [(-(KX,VX))|_],VX) :- K==KX.
get2(K, [_|T],R) :- get2(K,T,R).

put2_(-(K,V),[],Replaced,R) :- Replaced->R=[];R=[-(K,V)].
put2_(-(K,V),[-(KX,_)|T],_,[-(K,V)|RX]) :- K==KX,put2_(-(K,V),T,true,RX).
put2_(-(K,V),[H|T],Replaced,[H|RX]) :- put2_(-(K,V),T,Replaced,RX).

remove2_(_,[],Acc,Acc).
remove2_(K,[-(KX,_)|T],Acc,R) :- K==KX,remove2_(K,T,Acc,R).
remove2_(K,[H|T],Acc,R) :- remove2_(K,T,[H|Acc],R).

put2(-(K,V),Map,R) :- put2_(-(K,V),Map,false,R).
remove2(K,Map,R) :- remove2_(K,Map,[],R).

merge2(Map1,[],Map1).
merge2([],Map2,Map2).
merge2([-(K,V)|T],Map2,R) :- put2(-(K,V),Map2,RX),merge2(T,RX,R).

update_reg(-(reg(ToRegister),reg(FromRegister)),Registers,UpdatedRegisters) :- get2(FromRegister,Registers,Value),
                                                                               update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters).
update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters) :- put2(-(ToRegister,Value),Registers,UpdatedRegisters).
equate(LHS,LHS,0).
equate(LHS,RHS,1) :- LHS < RHS.
equate(LHS,RHS,-1) :- LHS > RHS.

exec([],Registers,Flag,TraceAcc,TraceAcc,Registers,Flag).
exec([mvc(reg(ToRegister),Value)|T],Registers,Flag,TraceAcc,FinalTrace,FinalRegisters,FinalFlag) :- 
                                                        update_reg(-(reg(ToRegister),Value),Registers,UpdatedRegisters),
                                                        exec(T,UpdatedRegisters,Flag,TraceAcc,RemainingTrace,FinalRegisters,FinalFlag),
                                                        FinalTrace=[mvc(reg(ToRegister),Value)|RemainingTrace].
exec([cmp(reg(CmpRegister),CmpValue)|T],Registers,_,TraceAcc,FinalTrace,FinalRegisters,FinalFlag) :- 
                                                        get2(CmpRegister,Registers,RegisterValue),
                                                        equate(RegisterValue,CmpValue,UpdatedFlag),
                                                        exec(T,Registers,UpdatedFlag,TraceAcc,RemainingTrace,FinalRegisters,FinalFlag),
                                                        FinalTrace=[cmp(reg(CmpRegister),CmpValue)|RemainingTrace].

exec([Instr|T],Registers,Flag,TraceAcc,FinalTrace,FinalRegisters,FinalFlag) :- 
                                                        exec(T,Registers,Flag,TraceAcc,RemainingTrace,FinalRegisters,FinalFlag),
                                                        FinalTrace=[Instr|RemainingTrace].
