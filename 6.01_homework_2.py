from lib601.sm import *

class CommentsSM(SM):
    startState = 'not_comment'

    def getNextValues(self, state, inp):
        if inp in ("\n", "#"):
            if state == "comment":
                output = None
                nextState = "not_comment"
            else:
                output = inp
                nextState = "comment"
        else:
            if state == "comment":
                output = inp
                nextState = "comment"
            else:
                output = None
                nextState = "not_comment"

        return (nextState, output)



class RibosomeSM(SM):
    def __init__(self):
        self.startState = ['notORF', [] ]
        self.rnatoAminoAcid = {"UUU":"Phenylalanine", "UUC":"Phenylalanine", "UUA":"Leucine", 
    "UCU":"Serine", "UCC":"Serine", "UCA":"Serine", "UCG":"Serine",
    "UAU":"Tyrosine", "UAC":"Tyrosine", "UAA":"STOP", "UAG":"STOP",
    "UGU":"Cysteine", "UGC":"Cysteine", "UGA":"STOP", "UGG":"Tryptophan",
    "CUU":"Leucine", "CUC":"Leucine", "CUA":"Leucine", "CUG":"Leucine",
    "CCU":"Proline", "CCC":"Proline", "CCA":"Proline", "CCG":"Proline",
    "CAU":"Histidine", "CAC":"Histidine", "CAA":"Glutamine", "CAG":"Glutamine",
    "CGU":"Arginine", "CGC":"Arginine", "CGA":"Arginine", "CGG":"Arginine",
    "AUU":"Isoleucine", "AUC":"Isoleucine", "AUA":"Isoleucine", "AUG":"Methionine",
    "ACU":"Threonine", "ACC":"Threonine", "ACA":"Threonine", "ACG":"Threonine",
    "AAU":"Asparagine", "AAC":"Asparagine", "AAA":"Lysine", "AAG":"Lysine",
    "AGU":"Serine", "AGC":"Serine", "AGA":"Arginine", "AGG":"Arginine",
    "GUU":"Valine", "GUC":"Valine", "GUA":"Valine", "GUG":"Valine",
    "GCU":"Alanine", "GCC":"Alanine", "GCA":"Alanine", "GCG":"Alanine",
    "GAU":"Aspartic Acid", "GAC":"Aspartic Acid", "GAA":"Glutamic Acid", 
    "GAG":"Glutamic Acid", "UUG":"Leucine",
    "GGU":"Glycine", "GGC":"Glycine", "GGA":"Glycine", "GGG":"Glycine",}

    def getNextValues(self,state,inp):
        # If last three letters read is AUG, ORF Start
        if "".join(state[1][-3:]) == 'AUG' and state[0] == "notORF":
            nextState = ['ORF', [inp]]
            output = self.rnatoAminoAcid['AUG']
        # Else still notORF, append input to state
        elif state[0] == "notORF":
            state[1].append(inp)
            nextState = ['notORF', state[1]]
            output = None

        # If State is ORF, begin reading
        elif state[0] == 'ORF':
            # If three letters read, return protein or None and change state
            if len(state[1]) == 3:
                seq = "".join(state[1])
                # If stop codon
                if self.rnatoAminoAcid[seq] == "STOP":
                    output = None
                    nextState = ['notORF', []]
                # Else protein
                else:
                    output = self.rnatoAminoAcid[seq]
                    nextState = ['ORF',[inp]]
                    
            # Else return None and incomplete read
            else:
                output = None
                state[1].append(inp)
                nextState = ['ORF', state[1]]

        return [nextState, output]





   
        
        
            

