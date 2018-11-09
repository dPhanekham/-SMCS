import math
import array

def main():
  #f = open('test1', 'r')

  with open('rabbit.svg', 'r') as f:

    b1 = array.array('B', [])
    string1 = ""
    string2 = ""
    fileIn1 = True    
    while fileIn1:
      fileIn1 = f.read(1)
      fileIn2 = f.read(1)
      string1 = string1 + fileIn1
      string2 = string2 + fileIn2
    b1 = array.array('B', string1)
    b2 = array.array('B', string2)
    p = array.array('B', [])
    print("B1 " + str(len(b1)))
    print(b1)
    print("B2 " + str(len(b2)))
    print(b2)

    #create parity string
    for i in range(len(b1)):
      if i < len(b2):
        p.append(b1[i] ^ b2[i])
    print("P " + str(len(p)))
    print(p)
    

    b2_recreated = array.array('B', [])
    for i in range(len(b1)):
      if i < len(p):
        b2_recreated.append(b1[i] ^ p[i])

    print("b2_rec " + str(len(b2_recreated)))
    print(b2_recreated)

    result = array.array('B', [])
    for i in range(len(b1)):
      result.append(b1[i])
      if i <  len(b2_recreated):
        result.append(b2_recreated[i])

    print(len(result))
    print(b2_recreated[len(b2_recreated)-1])
    with open('result.svg', 'w') as f2:
      f2.write(result.tostring())




if __name__ == "__main__":
  main()
