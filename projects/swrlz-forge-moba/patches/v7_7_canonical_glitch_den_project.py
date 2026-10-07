"""§wyrl§ Engine v7.7: promote the authored revision-142 Dragon Glitch Den project to the sole starter."""
import base64, gzip, json

PAYLOAD_B64="H4sIAOdOxmoC/+2d3ZLiRpbH7/cpFD0RuzcNzu+PvWu3PT2z657o6HLYFxMTHUISIBASJYmvmnDEPsS+gx9h7v0o+ySbAsquFBJQVSAEfbiwGyWVklKZP/3PyZN5/vlvjvMmiAdhHLz5T+fNb78uVmn026/O9+tDzm//cj664yB15rLL37wtfjwP0ixMYvNrc2h9ZJomo8DLzZF/mq/mQOxO1rV9l7qDJP6PzPkuiJ3/+5//de6CwHfeD91JL0jXtZkf58FkGrn5+g/89R9kHT+IH4vHYezXFAXxPEyTeBLE+R+/WP/AlP+yvrTAD/Mk/ePK8tSNs36STu6mrrc+5SJJI/+xxix2p9/Hbi8KinPm6Sz4/SLT1A3ju7ryeRgsPib+usYozB/r80xDpO5PprAomJqWm5qGCufB4w/SYB5uWxMz8vtlZ16wfh7bq+653niQJrNNS/wJI+QR9FjFwp0Hf43NBc7dqHgo28NTNx9mRRW/bA+4nmmJ4sjf19+dbeXrsnBdsftlnK6GwULPtnVbD/PnoqGcD5vLeFKer6br8sFuSeBOipI4mJl2j54W9Uynsptw0xxJtK7LqsUdrK/6H0+OmUabudH7JFo/W+vn7tzN3fQuX+3WFKyCvwThYFj0lngWRU+KiouffnJT05X+6tcUvx+Gkf9Xf+dipkkW5ptn+PffjzoOelv75fd//8O699w9QTWZ567v/Gkd+G3tl8o6Ju7yL1NTB3rarnlueuFnNx4ElSXfuRO3puh9kkR+slh38ieFkbvu46WmniTz4G4arHvH06r6po5g/bS//2PYf/PjZlw+fcpeMpkmsSnMSq3w5sfHwf+m8q570SyYpmGcv4/cLCt3Hi+JotBcwWfXD2dZ6eImmz94endpkOVhPts+UdQlvOoaH+/06V/2kt47g0Tzx2ueoC63Gm0We8O73PTUQT40xcoeFmFv/fSLcbU9/svb+vE+QAFCWb6sGu/vzXD2wsj5c5QkadWAN6A11zHz8lkanG/YP32ATwj/tBO/cVNvGOZB+UqKXlNc/Kf166XymZdA8iceMCn90/PEtHWeZjgZLazKX8KVDupi865QXD7+l6q3djkiVjmxynGXaeujGseRsP6uK63LI1eIpI3QKWTON++q++JRWLK67t1aA9iHikfifQyy4bEE++77v315MgZunWcuy8PBA8kq9YthD8DsCmFG98EMdxvHl95DLwnwAni9EF6RcFM6m0WVYiwNXGO+Ab/axi8DIGoBjJbxhWx8Sf70B+LF8CrISZD1wS/jmdrDMwU8A569kGdJigarIPeqePbj0FjwIMfahjNsupKltUqWGiJPC7kkzELSy2lmqtalz+nFGcAMYPZSmBHfu9cTj1XB7FNgngywrG0swwdYJmyWWcKNdemrlJm0WcZeBjO5B2YCYAYweyHMOJd+H/PKab5PSZq74PVvnaGpu9qyM3nZzsQlO9OiRUd29SvEGea2pUmAZ8Cz9vBMzkbLAcOLKp59DCZJugKeXaHjfz/RdFc27fnfxy8O/AJ+vZBfVYPqkV9PQ+acu3yv12w9EE8DMUOnTn/nPBU020TYdcqnPpZzx/Cs+fAu63KromScmtlmp2Yix6lxiDo1vgWnRqY71uuusvHqwtH289bglu+ZZzU4LkWNSAhiOxF6P7phXAqKPRl6P6yHJYS7bTgbz3oUe7NKJ957dx6ksfOzG0UOroJrmnjjywpEb32JnWwYRNGFwGkacaaIJP0FebUCJGhH8GEmqGJCScWxUqW5VEy7kiv65NM0gkjXgiK3v5Lulduw2yFwt+5f59OA1vH3W86chFG4q7n9kroBaE18b4CHYXIIWgSg1QC0MO/y8pyoopwyxTjHa2rZnjnzBxemFjXKr25UOI7oMm5TTCvA2EUxRrpY0VvDGJov0HyCeocwRgFjTWAM7WBMIEWFsQGxlAppZQfpd7Aw3erCGGPWNKrsYlBf7cIWQ+oGSKW9B+p77KCVyIBUDZCqjCkqNWWam/9TXswJ8DKmsIWpC5uIsitBXbUNU+hpKND1LheYTSepmuaHMMUBU+fH1E40hsRcIC6wUAQZNd8ySu03CcGvBQZhA2s1s4xFc6uJK/klgF/n51fZHlwjjDLFCRVEGkJhKltuD4IjCyzCM6FqNJVjiQ9bhBJQ1QCq+C6qsDEGFeaaC64Y41K1zAW/YxWC6womDs9NrX50T1k8fThELQXUOj+1CNqZNZRMI0SRMRC5ErRtsQ77TUTwa4GR2Ehkfzod34/ms0MM08CwBhiGd/a2oFJITBWSmiiKSjGj6vIMs01EcGyBgXgeXzxylwvURwcDSxFw6hKcYkRIQYVWihgMIWuTiE7bwkrBkQVzhmfilJ+vFtkCHTQJMUTAX4RTHCkpkSCmfi0VFzYGCMPij49sm0UIPi2wB89uD470qBeh/kGAQTT8RQCGqXlRUk60UBwLaQktdXmAlSNIwYkFBuFZODUf9vFgtLg/yCkId29iyrC0KyDCUmolMaFMIMyRjQVMLw0qWGcI04WNIyv3772lyMlBZEHceyNRDrs5PYrlOcW8IZJSUmsLriIaq83GIbi0wDxsgmFZhoPIS8ODDIOg+EaCSndCShXl5s0pheEYLk0XYtk++xBcWmAdngFToVbj/pgc9mJB7PtF1u4QRQkyLDKk0tpWLpenFKwwhNnChrbLijN/kdLDTiyIe28AUzsroRkzkOJMIsQUxqXZwjaoKVhjCPbgZQmm+igOk/RwvAPEwDdBMFwOghcSM0EIkYxgjuzpxPbZg+DFAovwTKBaxGNyHy7VQVBBoHsjoNrZdYZQgYsUZVRjrZBol/MdlhfCfGHjyJoO1DIfPxxEFoGY90aQpXcW5yCOKecCM8IkJ9JOqXj5KAdYYQgmYguUVx4ng2jsHcQYhMQ3gTHbBtxknFVGckmNmDA2ou3lal1IKbi1wEA8C6Y4G85dPDyMKQh8vwimOOZaEkQQ1VRqTFq1cgcWGMKUYTOYSqcxpvk4OIgpiHu/CKYYV5xSKgVBSNBSRsXW7zkDbi2wB89NsIf7ydI0wsHYLAJh8BchGDYyiwkqsGSaMCnaveMMeLHAIjwTqKqGWAlUOw/pDIliLd6cPFdsC2j2vFyxFSkmnZosbk5NWiSnJgmJU7Prv1Ozm7ZTs3WtU7M5pFOz4ZpTs8ORU7OjiFOzUN+pWRjr1Kw+c2pWdDg1IdROTcyiUxMJ5NRMvDs1s1tOjbvYqfHPODUGkWPJjGfl8LXfheYlSHkROqO0IhSVF+OXnA6YQcbeK3gHQsbepy85GswHeYYrX3I/ubMod+4it1f1ijOvEnMRs52E9s0rcivfuVWSFdd+zFvtT5RRRL2zSHV3HqtI6eHJc8oVCLKt+VJOOd21tDo9FaAMGNHTDz6eWLiU5ryUI51bN8i6V86xd9U989Ra/kiYfff9375kpdF8k1BDLomH8SIFqN0g1EgJapQD1YBqXwHVxin2mRlFQLXbo5phghBnmMEGpgHTWp1ChbvTVd97AKbdHtMMQWyoCYAaQO0rgJpapDiccwZQaz3U2uJS6wDUAGqthpqexn6vh2cAtduD2rlcakA1oFrLY3xizZZDAdOft0e1M7nUgGnAtJabn2E4ozmLgWk3x7RzudQAagC1lm88vlhKORmt6qH2OfwKmMYx63HdaqaVfPUlrDA7Czs+mTsNd7lEUgtKhNRMaSFOEFOLuqU9NQFeAK/nw4vJnN3zVQbwuiV4sbLXDNgF7Lo5dj3E49RFegLsuiF2kbIZyYFdwK7bMxoziZb3FAO7bohd+mQuMEAXoKut6KoaWBa6At/ZrpL9nCT9M+9BYLDUScunOcn+A+kszsNJcEUbEFSsmHVqFp05Ncs2nJrQZ6cmetCpCcBxaqawnZppIKfGk+rUOCmcGgPAsV6uL15gj0kX1c8cdFAZ9CcLIIYF9rDAvrFd3NN4ipSY7dlF5lMYRW56rTp0urn6o5QoQ9QIrbMo0bEeox6b9k6cmmK9z7smimEkCMeKE0JKO2Lx5ncbxfYezaUdsEBxnlhxTncGaEUGCnIDsIqWuQrzPgFYXQesdtLoIMkFlYQizrDSXDBgFbDqNll17w1XKzJbAquuRViJHWEluaSaU4WpooIwWkIFwApgdRuwGiVJnqoFA1hdibASZWGliWaUSoQx00ZZMUAVoOomUVU1hCpRlTUw6TCtONNJ5h0skl3DtEOFH9GpMdmdGnnsWG+iF7vtC8c8okhRjRkmiEtZ9ttz8NODn/7aYnS9oIenWeWekT8bUDl/S5JxM+psYYo7cfl0J5FpRdXrGzlKqPX72heiefIdZU0SW6HZrjCMXwOhUmXHcwh1S4ufyl9BlZ1Wlf3en28dTzwlefoQ6ko8hdnU+cnUaDSQ843zPg1c868qVg2DNKliVNG4zwDUNHJXQdrZwOClkKqrpKCUuaHKgmwapmHeWXeoowgmiS/7/T0EK05VRzHcxeq8FCthh5SiI16OMNo12oxrIjjlSktNm9VVGKF6mFnJEss4E3wfz+zVpEcgTRxC2nbYZI1n2ikdnfTcUsqR90M3db08SD+a+5mYq7GLi0H/07q3H8vLbz992f5RWMLDLjG77BaSJSYzN05kSCtN2cScKYycz7M4cL5zw0prdhr45j5t8faKTD6bU3ZMb8mD9CTi7igIal+SvRC8nIwr6y7LrdZ4cjFsdeMy8Uzhdcu3j24YOwYrk16QXl6+GRwVY6889G5zIUI8vX94kIMqEH0MJkm6MqpttUOaLYW8iqIXQ2iyPl3HNXeXvIZBbrkHbCse2mrc2cHeUcjyme5dA7KwrdkaJ1YpDbY9CXDlrq9Nr7+wMvu8fnbx4HcRdjzd3q0HScW4rpBbWhD+dMXLKZlnytWFdleLRKB5Vq2/Nlaq8y7yTNM241jzNufsLJJ0nE1dLzi9g217iu1dHcU6gb1+S1l3wMtWbAmumkYe+Nga9rHZXfrWpdoodFdLKSrXjP45SQeB8/MjPZz3SRqcXbAZWEV+pzcLi87SCQsN1X8duopOetzCUXHAe9YaMuEylnjzWJI2h3RpVSiosatRY5xYaLpiBTbq6RFf5H4VzX4cpuYqnR+DNC3z5GwKLF+fs5OZBj+99tpU/ng/125nFlOYh8TXxScIDNfqPWZFIYixF5PvGRLN7vn74EZvYUsi9OBP9bLSrPxvdxJG5uqdDd2qqJbvlryYZ8PZxI077iwfGrMyC6w5nGdRbXtRtwYtbMugDsaXJ5beq9P0dRNr+1K/K71g2wQsI8Y2F7w7RCtCam8BWDHp+4uZqIwt+5SGEzddOdtn+Ckwr5xmtNgWRdOdM55mQcC62uPmJwOJrmR+0lZg+uLxGWXaKvsrBf3ViP7aGUO7uusm1gYE4/5i3JtVRqH99utilUa//bolWSXDdkteTK/phpudyI0mr4xEM/06zivjzeZJ6AXbudKKmc1thW7s5slk1ZmbUV2KV5utfXWdfpLkHS+JzWgphfFMZlEedjLXPEDzsyDIbwuZtIxM1RWvgCYjFjTZS6mp3+79et3Q3Pzzwp66b5Neddzau2KwvasYa3ebsfJnM1Teb0fKcwXlptqf6Be8l8Wky6k8rX+PkX1ARk+d1SdGcqj9bDHJ8vr5imZ4bE9TrJH6FfH4imZKuvYyfNwlLwZyh9jhL89BMOVvD3wHCt80hXFXYnv7v1tBsj95mM4MEarDjk0bNIRkL/HDeNBJAzczbfP1QbnfVz3O2+knPRuTAcmA5JcjmXJRsyHrdSNZY5rcr5LKLBafkjR3I+cvbhQ53y/DvBnv63R91s7QnLUTlM96Eg+sa/ukijpMd3YNxdfnOwqhrhLetcYmsuZDgEqOBHxTU0vX4ox1D/lib8ETK+McEXcx2bOiZJPhojmibReAzIvTthhpot+TVznbhNkFNlYpzyjJsiYEpgHTTsS0lRz7pitX5nj9a9wPzFm2QdcNUi18PLExTdOgxVzjuo88dAXWLig1oNpXRLXJ2PMj975yT/W7qWlMY3v+VLjQnHe7a3LPsaAk25y0s/HbDV+3z9TRa0n6fcm9llqSvFva7lPwi67q3Ymq7t5YXPVXtZqEYWttL6K3sbRkmkgc5tPssFo7O9HWMUB/CLWmkCZ4X3i4lUgDogHRYH3cYYgJzJbhjFaanB+TJO6Hxtj8wS0W3cYOvtbN2aPNDRwr1HqM98+yO/t8lmcPveDV2WI71HZLka6UnHPJBeaCKI1Z0MHWclxcS5izOs/o233B2lfuO/uheO4GNu3YpeCxj9/6/gRL/95daeYeRSwCxGoHsQBYAKyvFFihSu7TxRwdBSwKwGqJxBLP4xUFXAGubgFXPS1HEU0GR+GKAa7agSugFdDqa6RVlOSZO3ZnR9GKA62uU1x1WN3e48Ar4NU18WoxXfA0FsujeCWAV1eprgBXgKvbwBWhQxWaMXEUriTgqiXySj+TVxgBsABYtwCsfIGSZdxTRwFLAbDaASzgFfDq6+SVdgmnnkZ7ks03lRirkYQK3nlSvRSWdczoBI+SV4snLLpYPP2Us7sjpLRWRAiEsBKMcwsE4iKpF0oLjHa/Q3Tp1USXUi1uI7j0IQuWeYT9rwRuPXqevSJOCDfMu4o+/dg7SHYREUhwLbFWSjGsLccXB7IB2YBsm7QyYzKaetOvhGz9Pu97uuWyjZVkm9iRbab7CcoxYpIYC9NOmSUBbgA3gFsxJPl86dLM9n7dMNwE6fc90W7ZRg/INkyNahNUKPNfpRmTpT3HgW3ANmCbGZHjfMldHD18LWw7015fpxRuZd1WSiNqZJsgxhhlSBcmKRO6DalOAW4At9bBTa+mob+asq8EbudKA3hCuLGSbqNlm5QiqrQq0rkoQomydN0l9jsEtAHa2oi2qgFZQtvnWRw4VU/3EXDrAXyi1IFB3EnN+bJDnAv8ME/STvnUewjoPd7BMQxsfu8dC9ZV09dOzcyPU+M3dWpcDk6NXHesN11lI9XtLlt2EO64CDHmmGmmlNSSKKJKUvMC28/W5pbGQOEqCn9YD7QjYXrz0SVqjLyRF0SVubHSJMudDzM39UO30byrl8216ktyJtE4nmBvwXT25rQb+xsuUcVqEgWtc1C9PKe0qZsg+8NOQKry9rJXyKrfg0Xv3Nj0uAmkYm0Z29y5acf8vjLS9/tJL0iBbS1kW3NoA7IB2a40tYliyzDujfauYXgXmYHt/PYvZxL6fhQ4eRhU7pw9DfygFW69P7rYcYmXpPBbzrJythLB63HzKpK9dL2CveUs2k1lAvQ69dqFbz99KfxQ37lhdvPW5SR9CPLcp8dxyktNJwBMXRxTAvFLg6k0oQCCCpB0KqMwM20oSWVWuHdZQRHng5sHBY/SwHBp6EZJJY7WySkvC6PtNRwX5xF4vWvI6UbtNZSdIrCtafwQq+tWf78FChUd/dpnOT/tjMOKnL3ktFOcmFxo48UYCyZm6X45labhfEuxa/VouRd3aJ07VSUWl8hUyfZlL7/OnG4tgRqkdLNRlY/dUa4f9u/B/7Ob+g7CZw81WyRp5Hd6s7DoNJ2w2DegSBffyHJ24V9lKl2MmpddxvIkNqBICVCC3AKhtpEN6+4P2ZCuK8pMJXwWqvGwimtrnH2KTDsNa6gGPqyzU4xenmKsnFjubakYIAYurFcwKPG9JOfIO0JbEUiV2zSQWJcrJgnTQiqFid6nsnSXYkQp4VxgwrjSILlAcp1Gct1oSt2UJdgdDJYH9RcB/dUG3NGW4Q60GWizs0ZmRSlJaLo6QptR8HtdhFjSvBsVYUgRiRHBWu5TaNz8+AmyQKCBQAOfWJl540X00BtNDmoyCpqsFYSj7SIcaDLQZOfkUzZGUd+jx/jLGPjLLg0rtU+OmW6itBCSMaokN+ASIMhAkIHHbA/9PERDMhzRg+qMgTprBfBo24AH+gz02VnDWsk9y1bLwRH6jIPPrBVefrxPpHUoTGuCSAOv2QGrFE39cNqfHdRlHHRZKxhH28Y40GWgy85JqCHuL90gio/QZQL8Zk3jSne5eRkyjorN/jXlPOhgsVeWMQjpByEG3rID6cyXTI8m6KAqE6DKWoM5ennMgRYDLXZOLgmXySjx0RFaTIKP7CKk6pQMSKWf4yTTSII4A3EGXrIS9/TMT8LJYS+ZBD3WDsrR1lEOtBlos3MyyhgmaDSk/AhtpsBP1jiwnhXvX4q3QJqCKgNVBi6zPfiLXSPRcJgclGgKJFo7iEfbRjxQaKDQzomoaJRNFJnRIxSaBu9ZO6ClnrEsUykOMg1kGjjPbOzxwYhPPffwZmUalFk7IEfbBjlQZqDMzuo7W/a5SGVyWJlhBL6zSzv7NYHdzECTgevsZLuZDQhX/cnikECrZh8ItOaBB/uZgT77qtYAuP59X96T+vzgd9PiUcEm/hcCVpFIpJTU1grAuEC8hbZzJd1ikhHwil1xSNl4ks1jPDiENAJIuxDSZFnGkFLOb3JxqGGAGkCtRVAb4SmfsT4+BDXYdLadOs3IJG19xIURh7sSEAeIaxHiVtmApEu/cinAD0E/3+Tt/TZwvSQ+O+UmwSRJVx3TrYZJ+kq2Wce2FZcmH9ZPwjRmGHVMv8vrEg6Wgegz3Wuvp600+Wn76vEFwtCUfQXlC1QcEHiNCNTCmjzAt4FDd4xkL8miKhz+l+sHjTnmIjeaGJ3XD8x9NThtKnhfeLiVbAOfHIANtN1zYNbn/WQgh4sDMCMAs+ZhBt44wBng7Fk4exhpN4567gGcUcBZ27QZ+OEAbgC3/asKMnc8v1/2q+D2uRjH4Ii7Jkcc+OEAgeCHezkOxxPsLZjO9q5g2D5057d/Oe8iM+6df3c+zMyDD93Y+RSk3jDIqki5Hs/NhPcGfpgnaWdzxmOY1jzMLGJ/UWPkjbwgKpH8izsvwHyvyselYssw7o3KxyfpQ5DnPq2+6RpootIKesos0XiMYjsjQS1z2P5yheT8uQgo+OZD0RtOzskP9d19F3c3H+w7n+XZQy8Y7kWZQdinNPGCLDP3Yt5fP7iFDIqBX8/kl8CGRzO6KvNo6d+7K83c8vFQJffpYo7Kx3tajiKaDMrHoyQ3Qt2dlY8vpguexmJZPk7oUIWGduXj+QIly7inXsNHbNvUekdxAiGBkK0h5Pr///i34l+//D+77vhXnEQCAA=="

def _once(s,old,new):
    if old not in s: raise RuntimeError("v7.7 token missing: "+old[:180])
    return s.replace(old,new,1)

def apply(html):
    s=html
    for a,b in {
      "V7_6_DESKTOP_EDITOR_POLISH":"V7_7_CANONICAL_GLITCH_DEN_PROJECT",
      "Maker v7.6":"Maker v7.7","MAKER v7.6":"MAKER v7.7",
      "v7.6 · DESKTOP EDITOR POLISH":"v7.7 · CANONICAL GLITCH DEN",
      "version:'v7.6'":"version:'v7.7'",
      "version:'swyrl-engine-agent-v5.6'":"version:'swyrl-engine-agent-v5.7'",
      "engine:'§wyrl§ Engine · Maker v7.6'":"engine:'§wyrl§ Engine · Maker v7.7'",
      "version:7.6":"version:7.7",
    }.items(): s=_once(s,a,b)

    payload=gzip.decompress(base64.b64decode(PAYLOAD_B64)).decode("utf-8")
    data=json.loads(payload)
    assert data["editor"]["revision"]==142 and len(data["scene"]["actors"])==120
    data["engine"]="§wyrl§ Engine · Maker v7.7"
    data["version"]=7.7
    data["project"].update({"name":"Glitch Dragon Den — Moonfire Sanctum","template":"glitch-dragons-den","kind":"dragons-den","environment":"dragon-den"})
    canonical=json.dumps(data,separators=(",",":"),ensure_ascii=False).replace("</","<\\/")

    # Replace the project chooser with one authoritative Dragon Glitch Den starter.
    start=s.index('<div class="project-grid">')
    end=s.index('</div>',start)+6
    card='''<div class="project-grid"><button class="project-card den" data-project-template="glitch-dragons-den"><span class="project-icon">🐲</span><strong>Glitch Dragon Den — Moonfire Sanctum</strong><span class="template-tag">CANONICAL STARTER</span><p>The authored 120-actor Dragon Glitch Den, promoted directly from the saved §E project.</p><span class="hint den-glow">Open Moonfire Sanctum</span></button></div>'''
    s=s[:start]+card+s[end:]

    # Keep one template route: every Dragon Den starter request resolves to this saved project.
    marker="function createProjectFromTemplate(template,force=false){"
    i=s.index(marker)
    body=s.index("\n}",i)+2
    old=s[i:body]
    new='''function createProjectFromTemplate(template,force=false){
  if(dirty&&!force&&!confirm('Open the canonical Glitch Dragon Den and discard unsaved scene changes?'))return;
  loadCanonicalGlitchDen();
  $('projectHub').classList.remove('show');
}'''
    s=s[:i]+new+s[body:]

    # Embed the exact saved project so boot/template opening does not depend on network fetches.
    js='''\nconst CANONICAL_GLITCH_DEN_PROJECT='''+canonical+''';
function loadCanonicalGlitchDen(){
  const p=structuredClone(CANONICAL_GLITCH_DEN_PROJECT);
  loadProject(p);
  currentProject={...p.project};
  initializeHistory('Opened canonical Glitch Dragon Den');
  markSaved();
  editorLog('Canonical Glitch Dragon Den opened · authored revision 142 · 120 actors','ok');
  toast('Glitch Dragon Den · Moonfire Sanctum');
}
'''
    s=s.replace("function createProjectFromTemplate(template,force=false){",js+"\nfunction createProjectFromTemplate(template,force=false){",1)

    # Startup must open the canonical authored project rather than a procedural legacy Den.
    for oldcall in ["buildGlitchDragonsDenProject();","buildDragonsDenProject();"]:
      idx=s.rfind(oldcall)
      if idx!=-1:
        s=s[:idx]+"loadCanonicalGlitchDen();"+s[idx+len(oldcall):]
        break
    else: raise RuntimeError("v7.7 startup project call missing")

    s=s.replace("defaultProject:'glitch-dragons-den'","defaultProject:'glitch-dragons-den',canonicalStarter:'moonfire-sanctum-r142'",1)
    s=s.replace("editorLog('§wyrl§ Engine v7.6 initialized · desktop editor polish','ok')","editorLog('§wyrl§ Engine v7.7 initialized · canonical Moonfire Sanctum starter','ok')",1)
    return s
