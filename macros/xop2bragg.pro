; ===================== XOP MACRO ===================================
;
; === AUTHORS ===
; Manuel Sanchez Del Rio (ESRF)
; Mauro Rovezzi (ESRF)
;
; === DESCRIPTION ===
; interactive generation of xcrystal.bragg ===
;
; === USAGE ===
; - Run xop
; - From menu: Tools -> XOP macro
; - Load Macro
; - Run
; ===================  write xcrystal.bragg ==========================
;
jump = 0
if (jump EQ 0) then begin
tmp = 0
tmptmp = temporary(tmp)
IF N_Elements(tmp) EQ 0 THEN tmp = xop_defaults('xcrystal_bent')
;tmp.bragg.parameters.emin = 5000.0
;tmp.bragg.parameters.emax = 150000.0
;tmp.bragg.parameters.estep = 1000.0
;tmp.bragg.parameters.estep = 1000.0
;tmp.bragg.parameters.ilattice[0] = '3'

; interactive selection of crystal
tmp2 = tmp.bragg 
tmp3 = bragg_inp(tmp2,ask=2)
 
; calculate structure 
tmp4 = bragg_calc(tmp3)

; write structure to file
bragg_out,tmp4
endif

;end
