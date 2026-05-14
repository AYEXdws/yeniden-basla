export const storyData = [
  {
    id: "intro",
    type: "intro",
    eyebrow: "1919 — AMASYA",
    title: "Amasya’da Tarihin Dönüm Noktası",
    text: [
      "Mondros Ateşkes Antlaşması’nın ardından Anadolu’nun birçok bölgesi işgal altındadır.",
      "Halk umutsuzdur. Saray baskı altındadır. İşgal kuvvetleri Anadolu’daki hareketleri izlemektedir.",
      "Sen, Mustafa Kemal Atatürk ile birlikte Amasya’da bulunan genç bir komutansın."
    ],
    button: "Hikâyeye Başla",
    next: "decision-1"
  },
  {
    id: "decision-1",
    eyebrow: "KARAR 1",
    title: "Toplantının Gizliliği",
    text: [
      "Hazırlanan bildirinin İngilizler ve İstanbul Hükûmeti tarafından öğrenilmesi büyük risk taşımaktadır.",
      "Bu toplantı nasıl yürütülmeli?"
    ],
    choices: [
      {
        label: "Toplantıları gizli yürüt",
        result: "Sadece güvendiğin komutanlarla çalışırsın. Genelge güvenli biçimde hazırlanır.",
        score: 2,
        next: "decision-2"
      },
      {
        label: "Daha fazla kişiyi dahil et",
        result: "Fikir çeşitliliği artar; ancak bilgi sızdırma riski yükselir.",
        score: 0,
        next: "decision-2"
      }
    ]
  },
  {
    id: "decision-2",
    eyebrow: "KARAR 2",
    title: "Genelgenin En Güçlü Mesajı",
    text: ["Millete verilecek mesaj belirlenmektedir."],
    choices: [
      {
        label: "Milletin azim ve kararını merkeze al",
        result: "Halkın kendi gücüne olan inancı artar ve Millî Mücadele’nin temel ilkesi ortaya konur.",
        score: 2,
        next: "decision-3"
      },
      {
        label: "Dış destek umudunu öne çıkar",
        result: "Kısa vadede umut verse de asıl çözümün milletin iradesi olduğu gerçeği zayıflar.",
        score: 0,
        next: "decision-3"
      }
    ]
  },
  {
    id: "decision-3",
    eyebrow: "KARAR 3",
    title: "Sivas Kongresi Çağrısı",
    text: ["Genelgede ülke çapında bir kongre toplanması önerilecektir."],
    choices: [
      {
        label: "Derhâl çağrı yap",
        result: "Tüm illerden temsilciler davet edilir. Anadolu’nun ortak sesi oluşur.",
        score: 2,
        next: "decision-4"
      },
      {
        label: "Bekle ve koşulları gözle",
        result: "Zaman kaybı yaşanır ve direnişin örgütlenmesi gecikir.",
        score: 0,
        next: "decision-4"
      }
    ]
  },
  {
    id: "decision-4",
    eyebrow: "KARAR 4",
    title: "Halkla İletişim",
    text: ["Amasya Genelgesi’nin Anadolu’ya ulaştırılması gerekmektedir."],
    choices: [
      {
        label: "Telgraf hatlarını kullan",
        result: "Mesaj Anadolu’nun dört bir yanına hızla yayılır.",
        score: 2,
        next: "final"
      },
      {
        label: "Yalnızca yerel duyurular yap",
        result: "Etki dar kalır ve ulusal koordinasyon gecikir.",
        score: 0,
        next: "final"
      }
    ]
  },
  {
    id: "final",
    type: "final",
    eyebrow: "FİNAL",
    title: "Millî İrade Doğuyor",
    text: [
      "Amasya Genelgesi başarıyla yayımlanır.",
      "Erzurum ve Sivas kongrelerinin yolu açılır.",
      "Kurtuluş Savaşı’nın temelleri atılır."
    ],
    quote: "Bir milletin kaderi, Amasya’da alınan cesur kararlarla değişti."
  }
];
