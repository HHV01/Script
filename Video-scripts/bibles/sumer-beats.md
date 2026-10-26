# BẢNG BEAT: SUMER

Bản 2. Ngày 22 tháng 10 năm 2026. 253 beat cho 20 phút 55 giây. Mỗi beat là một hình. Mốc thời gian căn theo file VO thực tế `Voice_sumer_full.wav`.

## Thông số

| Mục | Giá trị |
|---|---|
| Tổng beat | 253 |
| Tổng thời lượng | 20:55 |
| Trung bình | 4,96 giây một beat |
| Nguồn lời | `sumer-script-clean.md` |
| Nguồn thời gian | `Voice_sumer_full.wav`, 20:55.05 |
| Tốc độ đọc | khoảng 230 từ/phút |
| Một beat | một ảnh, một prompt ở State 5 |

Mốc thời gian căn theo word timestamps của file VO thực tế, không theo tốc độ ước tính. File VO dài 20:55.05 cho 4.816 từ sau khi cắt 5 cụm không có trong audio, tương đương khoảng 230 từ/phút. Vì vậy beat ngắn hơn bản cũ, trung bình 4,96 giây.

Mốc trong bảng làm tròn xuống giây. Beat rất ngắn, ví dụ hai lần chốt chữ Muối, có thể trùng mốc với beat ngay sau. Cột giây chính xác nằm trong file CSV.

## Cách đọc

- **NV**: T Tích, N Nông Dân, S Thư Lại, V Vua, E quần chúng, P tư tế, X lính, G Gilgamesh, K Enkidu, U Utnapishtim, H Humbaba, B bò thần, F vợ Utnapishtim, R Rawlinson, dấu trừ là không có người.
- **Bối cảnh**: plain, gate, zig, canal, field, marsh, tablet, dock, salt, temple, throne, market, wall, ruins, myth, abstract, modern.
- **Máy**: wide, medium, close, insert, top, low, pan. Pan là ảnh rộng để pan khi dựng, không phải ảnh chuyển động.
- **Lời kể**: nguyên văn, dùng để đối chiếu. Bản nhập cho studio nằm ở `sumer-beats.txt`.

## Bối cảnh

Sáu plate gốc: uruk-gate, ziggurat-far, canal-dawn, tablet-house, river-dock, salt-flat. Các set còn lại là biến thể hoặc plate mở rộng, giữ cùng palette, cùng vật liệu bùn, sậy, gạch, đất sét.

| Mã | Plate gốc | Dùng ở | Mô tả ngắn |
|---|---|---|---|
| gate | uruk-gate | hồi 0, 1, 3, 5, 7, 8 | cổng thành Uruk, tường bùn, hào nước, trời trắng |
| zig | ziggurat-far | hồi 5 | ziggurat bậc thang, đền nhỏ trên đỉnh, bóng đổ dài |
| canal | canal-dawn | hồi 1, 2, 5, 7 | kênh đất, cửa cống, nước đục, bờ thấp |
| tablet | tablet-house | hồi 3, 4, 5, 8 | nhà bảng, bảng đất sét, bút sậy, kho |
| dock | river-dock | hồi 1, 5 | bến sông, thuyền sậy, thuyền chở hàng |
| salt | salt-flat | hồi 0, 7 | đồng muối trắng, đất nứt, không cây |
| plain | plate mở rộng | hồi 0, 1, 8 | đồng bằng trống, đất nứt, không bóng người |
| field | canal-dawn, biến thể ruộng | hồi 1, 3, 7 | ruộng lúa mạch, bờ đất, nắng gắt |
| marsh | canal-dawn, biến thể đầm lầy | hồi 1, 2 | đầm lầy sậy, nước tù, bùn non |
| market | uruk-gate, biến thể chợ | hồi 3, 5, 7 | chợ bùn, hàng rổ, không tiền xu |
| temple | ziggurat-far, biến thể nội thất | hồi 2, 4, 7 | đền bùn, tượng thần nhỏ, kho lúa |
| throne | ziggurat-far, biến thể nội thất | hồi 4, 5 | phòng vua, bục đất, rèm vải, mũ vàng |
| wall | uruk-gate, biến thể tường | hồi 3, 5, 6, 8 | tường thành, cổng, lính, gạch nung |
| ruins | salt-flat, biến thể gò đất | hồi 8 | gò đất tell, tường đổ, bụi, nắng chiều |
| modern | không, set khung của Tích | hồi 8 | bàn gỗ tối, cửa sổ, đồng hồ cơ, hợp đồng |
| myth | không, set thần thoại | hồi 6 | nền xanh đêm, cát vàng, bóng đổ lớn, không kiến trúc thật |
| abstract | không, graphic | map, biểu đồ | nền đất sét trơn, mũi tên, chữ nêm, không người |

`modern` là không gian khung của Tích, tách khỏi Uruk. Không đưa đồ hiện đại vào các set cổ. Hồi 6 là thần thoại, bức tường của Gilgamesh được phép dùng gạch nung như biểu tượng, không coi là bằng chứng lịch sử.

## Luật hình ảnh

- Tích chỉ xuất hiện ở mở hồi, câu hỏi, và đoạn kết. Không đứng trong cảnh chết chóc, chiến tranh, tang lễ.
- Tích mặc áo vàng hiện đại xuyên suốt, không đổi theo thời kỳ. Các nhân vật khác đổi outfit theo hồi, giữ nguyên mặt, mắt, tóc.
- Mỗi beat là một ảnh đơn. Không dùng montage, không ghép nhiều hành động trong một khung.
- Từ beat 179, hồi 6 chuyển vào không gian thần thoại, palette xanh đậm và vàng, vẫn nét 2D cartoon. Không đổi sang style khác.
- Gilgamesh, Enkidu, Utnapishtim là nhân vật một lần, không nằm trong 4 bible. Thiết kế ghi ở mục 5.
- Sargon dùng thân Vua Sumer, đổi mũ đồng và râu ngắn. Ur-Nammu dùng thân Vua, đổi mũ sừng.
- Nông Dân và Thư Lại là nguyên mẫu, không già đi theo thời gian. Đổi outfit theo hồi, không đổi mặt, tóc, mắt.
- Không vẽ Ishtar trực tiếp. Dùng sao tám cánh hoặc tượng nhỏ.
- Giữ luật hướng: sông phía tây, cổng phía đông, ziggurat ở giữa khi nhìn về bắc.

## 1. Bảng beat

### Hồi 0. COLD OPEN (0:00 đến 0:39)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 1 | 0:00 | Bạn đang đứng trên một đồng bằng không có đá. | Wide: đồng bằng trống, nắng gắt, Tích đứng một mình, áo vàng lạc lõng | T | plain | wide |
| 2 | 0:02 | Không có gỗ. Không có quặng. Không có một ngọn núi nào để lấy đá mà xây. | Pan: không đá, không cây, chỉ bùn nứt và vài bụi sậy | - | plain | pan |
| 3 | 0:06 | Chỉ có bùn, nắng, và hai con sông chảy song song về phía biển. | Wide: hai con sông song song, đường chân trời phẳng | - | plain | wide |
| 4 | 0:10 | Đây là nơi con người lần đầu tiên viết ra chữ. Lần đầu tiên xây thành phố. Lần đầu tiên nghĩ ra khái niệm nợ, khái niệm lương, khái niệm giờ. | Insert: bàn tay Thư Lại ấn sậy lên đất sét, viên gạch và bảng nợ xếp cạnh | S | tablet | insert |
| 5 | 0:18 | Và cũng là nơi con người lần đầu tiên hiểu ra một điều rất khó chịu: mọi thứ mình dựng lên đều có thể bị lấy đi. | Medium: Tích đứng trước thành phố bùn, nhìn bàn tay mình | T | gate | medium |
| 6 | 0:24 | Không phải bởi chiến tranh. Không phải bởi thần linh. | Close: bóng người trên tường bùn, không lửa, không binh khí | - | gate | close |
| 7 | 0:27 | Mà bởi thứ mặn nhất, tầm thường nhất, và không thể nhìn thấy bằng mắt thường. | Insert: mặt đất trắng mặn, tinh thể muối lấp lánh | - | salt | insert |
| 8 | 0:33 | Muối. | Close: hạt muối trên đầu ngón tay, nền tối, giữ 2 giây | - | salt | close |
| 9 | 0:33 | Câu chuyện này không bắt đầu bằng một vị vua. Nó bắt đầu bằng một vùng đất mà không ai muốn sống. | Wide: đồng bằng trống, Tích nhỏ bé giữa khung | T | plain | wide |

### Hồi 1. VÙNG ĐẤT SAI LẦM (0:39 đến 3:18)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 10 | 0:39 | Nếu bạn được chọn một nơi để khởi đầu một nền văn minh, đây là nơi cuối cùng bạn nên chọn. | Medium: Tích đứng trước ngã ba, một bên sông, một bên sa mạc | T | plain | medium |
| 11 | 0:44 | Vùng đất này nằm giữa hai con sông lớn, Tigris ở phía đông, Euphrates ở phía tây. Người Hy Lạp sau này gọi nó là Mesopotamia, nghĩa là vùng đất giữa các con sông. | Map: hai con sông Tigris và Euphrates, mũi tên đông tây | - | abstract | top |
| 12 | 0:54 | Người Sumer không gọi mình như vậy. Họ gọi vùng đất của mình là ki-en-gir, gần nghĩa với "vùng đất của những người có văn hóa". | Close: tay Tích vẽ chữ ki-en-gir trên cát | T | plain | close |
| 13 | 1:00 | Nhưng nhìn bằng mắt thường, nó không giống nơi của người có văn hóa. | Wide: thành phố bùn nhỏ, hào nước, trời trắng | - | gate | wide |
| 14 | 1:04 | Mùa hè, nhiệt độ có thể vượt bốn mươi độ. Mặt đất nứt thành những đường như mai rùa. Gió thổi cát vào mắt, vào tai, vào thức ăn. | Wide: mặt trời đỉnh đầu, đất nứt mai rùa, gió cát | - | plain | wide |
| 15 | 1:12 | Ruồi sinh sản quanh mọi vũng nước tù. | Insert: ruồi bay quanh vũng nước tù, nắng gắt | - | marsh | insert |
| 16 | 1:14 | Mùa xuân, hai con sông dâng lên. Nước không dâng đúng lịch. Có năm đến sớm, cuốn trôi ruộng vừa gieo. | Wide: lũ tràn bờ, nước đục cuốn ruộng vừa gieo | - | canal | wide |
| 17 | 1:20 | Có năm đến muộn, đất khô đến mức hạt giống nằm chết dưới lớp bùn cứng. | Insert: hạt giống khô nằm dưới lớp bùn cứng | - | field | insert |
| 18 | 1:24 | Và quan trọng nhất: ở đây không có đá. | Medium: Tích cầm hòn đá nhỏ, nhìn quanh, không có đá lớn | T | plain | medium |
| 19 | 1:26 | Không có đá để làm tường. Không có gỗ để làm mái. Không có quặng đồng trong lòng đất. | Pan: tường bùn, mái sậy, không đá, không gỗ | - | gate | pan |
| 20 | 1:31 | Mọi thứ cần thiết để xây một thành phố đều phải mang từ nơi khác đến, bằng lưng người hoặc bằng thuyền. | Wide: đoàn người vác đá, thuyền chở gỗ trên sông | E | dock | wide |
| 21 | 1:38 | Người ta vẫn thường kể rằng các nền văn minh lớn sinh ra bên những con sông màu mỡ. Điều đó đúng, nhưng chưa đủ. | Map: sông, phù sa, lúa, mũi tên tổ chức | - | abstract | top |
| 22 | 1:44 | Sông chỉ cho phù sa. Phù sa chỉ cho lúa. Lúa chỉ nuôi được người khi có ai đó đứng ra tổ chức. | Medium: ba lớp hình, sông, lúa, người đứng giữa | - | field | medium |
| 23 | 1:50 | Ở đây, thứ được tổ chức đầu tiên không phải là chiến tranh, không phải là tôn giáo. | Close: Tích giơ tay, dừng lại trước chữ chiến tranh | T | plain | close |
| 24 | 1:54 | Là nước. | Insert: giọt nước rơi vào lòng kênh khô | - | canal | insert |
| 25 | 1:55 | Nhưng trước khi nói về nước, hãy nhìn vào thứ họ có quá nhiều: bùn. | Wide: bãi bùn mênh mông, người đứng nhỏ | - | marsh | wide |
| 26 | 1:59 | Bùn ở đây không phải thứ bẩn. Nó là vật liệu xây dựng duy nhất. Họ trộn bùn với rơm, đổ vào khuôn gỗ, phơi nắng. | Medium: Nông Dân đổ bùn trộn rơm vào khuôn gỗ | N | marsh | medium |
| 27 | 2:05 | Thành một viên gạch. Gạch bùn rẻ, dễ làm, và rất yếu. | Insert: viên gạch bùn non, rơm lòi, nắng làm khô | - | marsh | insert |
| 28 | 2:08 | Một trận mưa lớn có thể làm tan chân tường. Một trận lụt có thể xóa sạch cả khu phố. | Wide: mưa lớn xối vào tường bùn, chân tường tan | - | gate | wide |
| 29 | 2:13 | Sau vài chục năm, một ngôi nhà thường phải đập đi làm lại. Thành phố không đứng yên. Nó lớn lên theo kiểu chồng các lớp đổ nát lên nhau. | Wide: ngôi nhà bùn đổ một nửa, nhiều lớp gạch cũ bên dưới | - | gate | wide |
| 30 | 2:20 | Các nhà khảo cổ ngày nay gọi đó là tell, những gò đất cao dần lên vì người ta xây lại trên chính đống đổ của mình. | Wide: gò đất tell giữa đồng bằng, vết cắt khảo cổ | - | plain | wide |
| 31 | 2:27 | Trong khi bùn là vật liệu của tường, sậy là vật liệu của mọi thứ còn lại. | Medium: Nông Dân bó sậy, sậy cao hơn đầu | N | marsh | medium |
| 32 | 2:30 | Sậy mọc dày ở đầm lầy, cao hơn đầu người. Người ta bó sậy làm mái nhà, đan thành thuyền, bện thành giỏ, làm cột, làm bàn, làm giường. | Wide: mái sậy, thuyền sậy, giỏ sậy xếp cạnh nhau | N | marsh | wide |
| 33 | 2:39 | Nhựa bitum, thứ đen và dính rỉ ra từ lòng đất, được dùng như keo và như lớp chống thấm. | Insert: nhựa bitum đen rỉ từ đất, bôi lên thuyền | - | marsh | insert |
| 34 | 2:44 | Con thuyền đầu tiên ở đây có thể chỉ là một bó sậy phủ bitum. | Medium: Nông Dân đẩy thuyền sậy phủ bitum xuống nước | N | dock | medium |
| 35 | 2:47 | Một nền văn minh được xây bằng thứ mọc lên và thứ rỉ ra. | Wide: thành phố bùn, sậy, khói, một mớ hỗn độn | - | gate | wide |
| 36 | 2:50 | Đó là lý do thành phố ở đây trông như một mớ hỗn độn gồm bùn, sậy và tro. | Close: bùn, sậy, tro trong cùng một khung | - | gate | close |
| 37 | 2:54 | Bạn sống trong một ngôi nhà mà bạn biết chắc nó sẽ tan. Bạn xây lại. Nó lại tan. Con bạn xây lại. Cháu bạn xây lại. | Wide: nhiều thế hệ bàn tay cùng xây một bức tường | E | gate | wide |
| 38 | 3:02 | Một nền văn minh hình thành từ thói quen xây lại. | Medium: Tích nhìn gò đất, hiểu ra thói quen xây lại | T | plain | medium |
| 39 | 3:05 | Và để xây lại đúng cách, bạn cần nhớ. Cần biết ai đã đóng góp bao nhiêu. Cần biết mùa nào trồng gì. Cần biết ai nợ ai. | Insert: tay khắc nợ lên đất sét, danh sách dài | - | tablet | insert |
| 40 | 3:11 | Sự tạm bợ sinh ra sổ sách. Sổ sách sinh ra chữ. | Close: chữ nêm đầu tiên, sổ sách | - | tablet | close |
| 41 | 3:16 | Nhưng chúng ta đang đi trước quá nhanh. | Wide: Tích quay lại nhìn hai con sông | T | plain | wide |

### Hồi 2. DẮT NƯỚC (3:18 đến 5:30)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 42 | 3:18 | Nước ở Mesopotamia không hiền. | Wide: sông dâng, nước đục, bờ thấp | - | canal | wide |
| 43 | 3:20 | Vào mùa lũ, nước dâng cao hơn đồng bằng vài mét. | Low: mặt nước cao hơn đồng bằng, đê đất | - | canal | low |
| 44 | 3:23 | Nếu để tự nhiên, nó sẽ tràn qua bờ, đọng lại thành những đầm lầy rộng, rồi rút đi, để lại một lớp phù sa và một vùng nước tù đầy muỗi. | Wide: lũ tràn, đầm lầy, muỗi, nước tù | - | marsh | wide |
| 45 | 3:31 | Nước tràn là nước chết. Nước đứng yên là nước chết. | Insert: nước đứng yên, váng, ấu trùng | - | marsh | insert |
| 46 | 3:34 | Người Sumer học được một điều mà sau này mọi nền văn minh tưới tiêu đều phải học: nước phải chảy. | Medium: Nông Dân đứng bên kênh, nước chảy qua mương | N | canal | medium |
| 47 | 3:39 | Họ đào kênh. Không phải một con kênh. Một mạng kênh. Kênh chính dẫn từ sông vào đồng bằng. Kênh nhánh tỏa ra từng cánh đồng. | Top: mạng kênh như mạch máu, kênh chính, nhánh | - | abstract | top |
| 48 | 3:46 | Cống nhỏ đưa nước vào từng thửa. Đê chặn nước lũ. Cửa cống mở đúng lúc. | Close: cửa cống mở, nước tràn vào thửa | - | canal | close |
| 49 | 3:51 | Nghe thì đơn giản. Nhưng để làm được, cần một thứ chưa từng tồn tại: một lịch. | Medium: Thư Lại nhìn trời, cầm thẻ đếm, cần lịch | S | canal | medium |
| 50 | 3:56 | Bạn phải biết khi nào lũ đến. Bạn phải biết khi nào mở cống. | Map: mặt trời, mực nước, lịch, ba biểu tượng | - | abstract | top |
| 51 | 4:00 | Bạn phải biết bao nhiêu người cần có mặt để đào một đoạn kênh dài vài trăm mét. | Wide: đoàn người đào kênh dài hàng trăm mét | E | canal | wide |
| 52 | 4:04 | Và bạn phải biết ai chịu trách nhiệm khi đoạn kênh đó bị bồi. | Close: bùn bồi, người chỉ tay vào đoạn kênh | E | canal | close |
| 53 | 4:07 | Vì kênh ở đây không tự làm sạch. Phù sa lắng xuống đáy. Sau một mùa, lòng kênh nông đi. | Insert: phù sa lắng đáy, lòng kênh nông dần | - | canal | insert |
| 54 | 4:13 | Sau vài mùa, nước không vào được nữa. Mỗi năm, hàng nghìn người phải ra đào bùn, khiêng đất, đắp lại bờ. | Wide: hàng nghìn người khiêng đất, đắp bờ | E | canal | wide |
| 55 | 4:20 | Đào kênh không phải việc của một làng. Nó là việc của nhiều làng, trong nhiều tuần, dưới một người chỉ huy. | Medium: người chỉ huy trên bờ, đội lao động bên dưới | E | canal | medium |
| 56 | 4:26 | Các tấm bảng ghi lại những đội lao động, số ngày công, khẩu phần phát ra. Có người làm việc cho đền. | Insert: bảng đất ghi ngày công, khẩu phần | S | tablet | insert |
| 57 | 4:31 | Có người bị trưng tập theo mùa. Cái mà chúng ta gọi là thuế, nghĩa vụ công dân, hay dịch vụ công, đều có tổ tiên ở đây. | Medium: Thư Lại ghi, Nông Dân nhận khẩu phần | S+N | canal | medium |
| 58 | 4:38 | Và thời gian bắt đầu được đo bằng một thứ khác ngoài mặt trời: bằng số ngày người ta phải làm. | Close: mặt trời lặn, thẻ ngày công, bóng dài | - | canal | close |
| 59 | 4:43 | Đây là công việc tập thể đầu tiên trong lịch sử nhân loại ở quy mô lớn. | Wide: công trường tập thể, hàng người, kênh dài | E | canal | wide |
| 60 | 4:47 | Và bất cứ khi nào con người phải làm việc tập thể ở quy mô lớn, họ cần một trung tâm. | Medium: đám đông quay về một trung tâm, ngôi đền | E | temple | medium |
| 61 | 4:52 | Trung tâm đó là ngôi đền. | Wide: đền bùn, cổng, kho, người ra vào | - | temple | wide |
| 62 | 4:54 | Người Sumer tin rằng đất thuộc về thần. Mỗi thành phố có một vị thần bảo hộ. Thần sở hữu ruộng, kênh, kho lúa, đàn cừu. | Medium: tượng thần nhỏ, ruộng, kênh, kho lúa | P | temple | medium |
| 63 | 5:01 | Người dân chỉ là người canh tác trên đất của thần. Đền không chỉ là nơi cầu nguyện. Nó là kho. Là xưởng. Là văn phòng. Là ngân hàng. | Wide: đền như kho, xưởng, văn phòng, ngân hàng | P+E | temple | wide |
| 64 | 5:08 | Các thầy tư tế ghi lại mọi thứ: ai nộp bao nhiêu lúa, ai lấy bao nhiêu bia, ai làm việc mấy ngày, ai nợ bao nhiêu. | Insert: thầy tư tế khắc bảng lúa, bia, ngày công, nợ | P | tablet | insert |
| 65 | 5:15 | Nghe quen không? | Close: Tích nhìn thẳng máy, hỏi nghe quen không | T | temple | close |
| 66 | 5:16 | Đó là bộ máy hành chính đầu tiên. Và nó ra đời không phải để cai trị con người. Nó ra đời để quản lý nước. | Top: bộ máy hành chính, đền, kho, bảng, nước | - | abstract | top |
| 67 | 5:22 | Ai giữ cổng nước, người đó giữ thành. | Medium: Nông Dân đứng ở cổng nước, tay giữ cống | N | canal | medium |
| 68 | 5:24 | Nhưng nước chỉ là một nửa câu chuyện. Nửa còn lại là thứ mà nước tạo ra khi được dắt đúng chỗ. | Wide: nửa khung là nước, nửa khung là lúa | - | canal | wide |

### Hồi 3. CỖ MÁY BIẾN LÚA THÀNH NGƯỜI (5:30 đến 8:08)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 69 | 5:30 | Lúa. | Close: hạt lúa mạch trên lòng bàn tay | - | field | close |
| 70 | 5:31 | Một héc ta lúa mạch thời đó, trong một năm tốt, có thể nuôi được nhiều người hơn một héc ta rừng săn bắn. | Wide: ruộng lúa mạch vàng bên rìa rừng săn bắn | - | field | wide |
| 71 | 5:36 | Đó là một phép tính đơn giản nhưng thay đổi mọi thứ. | Map: phép tính một héc ta, mũi tên nuôi người | - | abstract | top |
| 72 | 5:39 | Nếu bạn trồng lúa, bạn không cần đi săn mỗi ngày. Bạn không cần di chuyển theo đàn thú. Bạn ở yên một chỗ. | Medium: Nông Dân đứng yên giữa ruộng, không đi săn | N | field | medium |
| 73 | 5:45 | Bạn có thể dự trữ. Bạn có thể cho người khác ăn, và đổi lại, họ làm việc cho bạn. | Wide: kho lúa, người chia lúa, người làm việc | N+E | field | wide |
| 74 | 5:50 | Dư thừa là thứ sinh ra mọi thứ còn lại. | Insert: đống lúa dư, hạt tràn khỏi giỏ | - | field | insert |
| 75 | 5:52 | Với dư thừa, một người có thể chuyên tâm làm đồ gốm. Một người khác dệt vải. Một người khác rèn đồng. | Medium: thợ gốm, thợ dệt, thợ rèn đồng trong cùng một sân | E | market | medium |
| 76 | 5:58 | Một người khác đứng ra ghi chép. Một người khác chỉ huy. | Medium: thư lại ghi chép, người chỉ huy đứng sau | S+E | market | medium |
| 77 | 6:01 | Và một người có thể sống mà không tự trồng ra thức ăn. | Close: một người ngồi ăn, không cầm cuốc | E | market | close |
| 78 | 6:04 | Lần đầu tiên trong lịch sử, đó là một nghề. | Wide: thành phố mọc lên, nhiều nghề mới | - | gate | wide |
| 79 | 6:07 | Thành phố lớn lên từ đây. Eridu, có lẽ là nơi được người Sumer coi là thành phố đầu tiên. | Wide: Eridu, thành phố bùn đầu tiên, ziggurat nhỏ | - | gate | wide |
| 80 | 6:13 | Uruk, lớn hơn, có tường, có đền, có chợ. Vào khoảng năm 3000 trước Công nguyên, Uruk có thể là nơi tập trung đông người nhất trên Trái Đất. | Wide: Uruk lớn hơn, tường, đền, chợ, đông người | - | gate | wide |
| 81 | 6:21 | Ước tính rất khác nhau, nhưng có thể lên tới vài chục nghìn người. | Top: đám đông trong thành, vài chục nghìn người | - | gate | top |
| 82 | 6:24 | Hãy hình dung con số đó. | Medium: Tích đứng giữa đám đông, choáng | T+E | market | medium |
| 83 | 6:26 | Vài chục nghìn người sống trong một khu vực mà bạn có thể đi bộ qua trong một buổi sáng. | Wide: thành phố nhìn từ xa, người nhỏ như kiến | - | gate | wide |
| 84 | 6:30 | Không ai ở đó tự nuôi mình hoàn toàn. Người làm gốm đổi nồi lấy lúa. Người dệt vải đổi vải lấy bia. | Medium: Nông Dân đổi nồi lấy lúa với người thợ gốm | N+E | market | medium |
| 85 | 6:37 | Người chăn cừu đổi len lấy dao đồng. Người ghi chép đổi chữ lấy khẩu phần. | Medium: Thư Lại đổi bảng chữ lấy khẩu phần | S+E | market | medium |
| 86 | 6:41 | Thành phố là một cỗ máy biến lúa thành người, và biến người thành những thứ khác. | Map: cỗ máy, lúa vào, người và nghề ra | - | abstract | top |
| 87 | 6:46 | Chợ không cần tiền xu. Ở Sumer, đơn vị tính thường là lúa mạch. Một cái nồi đáng bao nhiêu lúa, một con cừu đáng bao nhiêu lúa. | Wide: chợ không tiền xu, lúa mạch làm thước đo | E | market | wide |
| 88 | 6:55 | Lúa mạch là tiền, là lương, là thước đo. Nhưng lúa không để được lâu. | Insert: lúa mạch đong trong bát, tem niêm phong | - | market | insert |
| 89 | 6:59 | Nó sinh ra một vấn đề mà mọi nền kinh tế sau này đều gặp: làm sao giữ giá trị qua thời gian. | Close: lúa mốc, mọt, thời gian trôi | - | market | close |
| 90 | 7:04 | Kho lúa, tem niêm phong, người giữ kho, và cuối cùng là chữ, tất cả đều ra đời để trả lời câu hỏi đó. | Wide: kho lúa, tem niêm phong, người giữ kho, bảng chữ | E+S | market | wide |
| 91 | 7:10 | Thành phố không chỉ là nơi trao đổi hàng hóa. Nó là nơi trao đổi lời hứa. | Medium: hai người bắt tay, lời hứa, không giấy | N+E | market | medium |
| 92 | 7:14 | Nhưng cỗ máy nào cũng có giá. | Close: bánh răng cỗ máy kẹt, nền tối | - | abstract | close |
| 93 | 7:16 | Khi mọi người sống chen nhau, nước thải chảy ra đâu? Rác đổ ở đâu? Xác chết chôn ở đâu? | Wide: thành phố chật, nước thải, rác, mộ | E | gate | wide |
| 94 | 7:21 | Những câu hỏi này chưa ai từng phải trả lời ở quy mô này. Dịch bệnh lây nhanh hơn bất kỳ tin đồn nào. | Insert: ruồi, bệnh, người nằm, trẻ con | E | gate | insert |
| 95 | 7:26 | Trẻ con chết nhiều. Phụ nữ chết khi sinh. Người yếu chết khi mùa màng thất bát. | Wide: đám tang trẻ bên thành phố, mùa màng thất bát | E | gate | wide |
| 96 | 7:31 | Và có một thứ mới, không thể tránh khỏi: bất bình đẳng. | Close: kho lúa lớn, người nghèo đứng ngoài | N+E | market | close |
| 97 | 7:34 | Trong làng săn bắn, của cải không tích lũy được nhiều. Bạn giỏi săn hơn, bạn vẫn không thể giữ được mười con hươu. | Wide: làng săn bắn, thịt hỏng, không tích lũy | E | plain | wide |
| 98 | 7:41 | Thịt sẽ hỏng. Ở thành phố, bạn có thể giữ được kho lúa. Kho lúa tạo ra quyền lực. Quyền lực tạo ra kho lúa lớn hơn. | Medium: kho lúa, quyền lực, kho lớn hơn | E | market | medium |
| 99 | 7:48 | Rồi chiến tranh. Thành phố này cần đất của thành phố kia. Người bại trận không bị giết hết. Họ bị bắt làm việc. | Wide: chiến tranh, thành phố cháy, tù binh | X+E | wall | wide |
| 100 | 7:54 | Chế độ nô lệ xuất hiện cùng lúc với chữ viết, gần như cùng một thế hệ. | Insert: bảng đất ghi tên người như tài sản | S | tablet | insert |
| 101 | 7:58 | Lần đầu tiên, một con người có thể được ghi trong một tấm bảng như một món tài sản. | Close: con số nợ khắc sâu, bàn tay run | - | tablet | close |
| 102 | 8:03 | Và cũng lần đầu tiên, một người có thể chết vì một con số. | Medium: Nông Dân cúi đầu trước bảng nợ | N | tablet | medium |
| 103 | 8:06 | Con số đó là nợ. | Close: chữ nợ hiện trên đất sét | - | tablet | close |

### Hồi 4. CHỮ BẮT ĐẦU BẰNG NỢ (8:08 đến 11:08)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 104 | 8:08 | Trước khi có chữ, người ta dùng những viên đất sét nhỏ. | Insert: những viên đất sét nhỏ, hình tròn, hình nón | - | tablet | insert |
| 105 | 8:11 | Một viên hình tròn có thể là một con cừu. Một viên hình nón có thể là một bình dầu. | Close: viên tròn là cừu, viên nón là bình dầu | - | tablet | close |
| 106 | 8:16 | Người ta bỏ những viên này vào một cái hộp đất sét, niêm phong lại, và vẽ lên vỏ hộp vài ký hiệu để biết bên trong có gì. | Medium: tay Thư Lại niêm phong hộp đất, vẽ ký hiệu lên mặt hộp | S | tablet | medium |
| 107 | 8:22 | Rồi ai đó nghĩ ra một ý tưởng tiết kiệm hơn: thay vì bỏ viên đất vào hộp, hãy vẽ luôn viên đất lên mặt hộp. | Insert: tay vẽ viên đất lên mặt hộp thay vì bỏ vào | S | tablet | insert |
| 108 | 8:29 | Đó là khoảnh khắc chữ viết ra đời. | Close: khoảnh khắc đầu sậy chạm đất sét | - | tablet | close |
| 109 | 8:31 | Không phải một bài thơ. Không phải một lời cầu nguyện. | Medium: Tích lắc đầu, không phải thơ, không phải cầu nguyện | T | tablet | medium |
| 110 | 8:34 | Một danh sách. | Insert: một danh sách dài trên bảng đất | - | tablet | insert |
| 111 | 8:35 | Khoảng năm 3200 trước Công nguyên, ở Uruk, người ta bắt đầu ấn một cây sậy vát nhọn lên đất sét ướt. | Wide: Uruk 3200 TCN, người ấn sậy lên đất sét | S+E | tablet | wide |
| 112 | 8:41 | Đầu sậy tạo ra một vết hình nêm. Ghép nhiều vết lại, thành một dấu. Ghép nhiều dấu lại, thành một từ. Ghép nhiều từ lại, thành một câu. | Close: vết nêm, dấu, từ, câu | - | tablet | close |
| 113 | 8:48 | Chữ hình nêm ra đời như vậy. Tên gọi của nó đến từ chữ Latin cuneus, nghĩa là cái nêm. | Medium: Thư Lại giơ bảng, chữ hình nêm | S | tablet | medium |
| 114 | 8:53 | Và những tấm bảng đầu tiên, gần như tất cả, là sổ sách. | Wide: kho bảng, toàn sổ sách xếp lớp | E | tablet | wide |
| 115 | 8:56 | Năm con cừu. Ba trăm lít lúa mạch. Mười hai người làm công. Hai bình bia. Một mảnh ruộng bên kênh phía bắc. | Insert: bảng kê cừu, lúa, người, bia, ruộng | - | tablet | insert |
| 116 | 9:02 | Đọc những tấm bảng đó hôm nay, bạn không thấy thần thoại. Bạn thấy một người quản lý kho đang cố nhớ xem tháng trước mình đã giao cho ai bao nhiêu. | Medium: người quản lý kho cố nhớ, tay trên trán | E | tablet | medium |
| 117 | 9:10 | Đó là khởi đầu của văn học nhân loại. Một phiếu xuất kho. | Close: Tích cầm bảng, gọi đó là phiếu xuất kho | T | tablet | close |
| 118 | 9:14 | Nhưng một khi bạn có thể ghi lại quá khứ, bạn có thể làm một việc nguy hiểm hơn: bắt người khác nhớ. | Medium: Thư Lại khắc lời hứa, bóng dài | S | tablet | medium |
| 119 | 9:20 | Một lời hứa miệng có thể bị quên. Một lời hứa khắc trên đất sét thì không. Nó nằm đó, trong kho, hai mươi năm sau vẫn còn. | Insert: lời hứa trên đất sét, hai mươi năm sau vẫn còn | - | tablet | insert |
| 120 | 9:26 | Con bạn sẽ đọc nó. Chủ nợ của bạn sẽ đọc nó. | Close: đứa trẻ và chủ nợ cùng đọc bảng | E | tablet | close |
| 121 | 9:29 | Chữ biến ký ức thành tài sản. | Map: ký ức biến thành tài sản, mũi tên | - | abstract | top |
| 122 | 9:31 | Hãy tưởng tượng một người nông dân. Mùa trước mất mùa. Ông ta vay ba trăm lít lúa từ đền, hứa trả sau vụ tới, lấy mảnh ruộng làm vật đảm bảo. | Wide: Nông Dân đứng trước đền, vay lúa, mùa mất | N | temple | wide |
| 123 | 9:38 | Vụ tới, nước đến muộn. Ông ta trả không đủ. Món nợ cộng thêm lãi. Đến mùa thứ ba, mảnh ruộng không còn là của ông. Ông thành người làm thuê trên đất cũ của mình. | Wide: Nông Dân đứng trên mảnh ruộng đã mất, bảng nợ trong tay | N | field | wide |
| 124 | 9:48 | Tất cả được ghi trên một tấm bảng, rõ ràng, hợp pháp, có người làm chứng, có con dấu. Không ai làm sai. Hệ thống vận hành đúng. | Insert: bảng nợ có con dấu, người làm chứng | S | tablet | insert |
| 125 | 9:55 | Và đó chính là điều đáng sợ. | Close: Tích nhìn bảng, lạnh người | T | tablet | close |
| 126 | 9:57 | Và nó tạo ra một tầng lớp mới: người biết chữ. | Wide: tầng lớp mới, người biết chữ, đứng trên đám đông | S+E | tablet | wide |
| 127 | 9:59 | Ở Sumer, đó là các thư lại. Họ học trong một ngôi nhà gọi là edubba, nghĩa là nhà bảng. | Medium: edubba, trẻ em ngồi, thầy giáo | S+E | tablet | medium |
| 128 | 10:05 | Trẻ em vào đó từ nhỏ, tập ấn sậy lên đất sét, chép đi chép lại những danh sách từ, những câu mẫu, những bài học đạo đức. | Close: tay trẻ ấn sậy, chép đi chép lại | E | tablet | close |
| 129 | 10:11 | Thầy giáo có quyền đánh. Học trò học thuộc lòng. Ai không theo được thì bị đuổi về làm ruộng. | Wide: thầy đánh, học trò cúi, đứa bị đuổi | S+E | tablet | wide |
| 130 | 10:17 | Nghe như trường học hiện đại, nhưng mục đích khác. Họ không học để hiểu thế giới. Họ học để kiểm soát nó. | Medium: Tích nhìn lớp học, học để kiểm soát | T | tablet | medium |
| 131 | 10:22 | Một người biết chữ có thể ghi ai nợ ai. Một người biết chữ có thể viết lại một thỏa thuận theo cách có lợi cho mình. | Insert: bảng nợ, thỏa thuận viết lại có lợi | S | tablet | insert |
| 132 | 10:29 | Một người biết chữ có thể đọc được lệnh của vua. | Close: lệnh vua trên bảng, con dấu | V+S | tablet | close |
| 133 | 10:32 | Và vua thì cần chữ hơn ai hết. | Medium: Vua ngồi, cầm bảng, cần chữ | V | throne | medium |
| 134 | 10:35 | Khoảng năm 2100 trước Công nguyên, một vị vua của Ur tên là Ur-Nammu cho khắc lên đất sét một bộ luật. | Wide: Ur-Nammu, bộ luật khắc đất sét | V+S | temple | wide |
| 135 | 10:41 | Đó là bộ luật cổ nhất còn lại đến hôm nay. Trong đó có những điều khoản về bồi thường, về hôn nhân, về đất đai, về tội giết người. | Insert: điều khoản bồi thường, hôn nhân, đất, giết người | - | tablet | insert |
| 136 | 10:48 | Luật không phải để công bằng. Luật là để một người cai trị hàng chục nghìn người mà không cần có mặt ở mọi nơi. | Medium: Vua không cần có mặt, luật thay mặt | V | throne | medium |
| 137 | 10:54 | Bạn không cần đứng trước mặt kẻ trộm để trừng phạt hắn. Bạn chỉ cần viết ra hình phạt. Người khác sẽ thi hành. | Wide: kẻ trộm bị xử, người thi hành, vua vắng | X+E | gate | wide |
| 138 | 11:00 | Chữ là công nghệ cai trị đầu tiên. | Close: chữ là công nghệ cai trị | - | tablet | close |
| 139 | 11:02 | Và nó cũng là công nghệ ghi nhớ cuối cùng. Khi mọi thứ khác biến mất, chữ vẫn nằm đó. | Wide: thành phố biến mất, bảng còn lại | - | ruins | wide |

### Hồi 5. THẦN, VUA, BÁNH XE (11:08 đến 14:08)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 140 | 11:08 | Ở giữa mỗi thành phố Sumer có một ngọn tháp. | Wide: ziggurat giữa thành phố, nắng chiều | - | zig | wide |
| 141 | 11:10 | Không phải tháp để nhìn xa. Cũng không phải lăng mộ. Đó là ziggurat, một nền đất hình bậc thang, càng lên cao càng nhỏ, trên đỉnh có một ngôi đền nhỏ. | Low: ziggurat bậc thang, đền nhỏ trên đỉnh | - | zig | low |
| 142 | 11:19 | Người ta tin rằng thần ngự trên đỉnh. Thầy tư tế lên đó để dâng lễ. Dân chúng đứng dưới chân tháp, nhìn lên, và thấy mình nhỏ. | Medium: thầy tư tế lên bậc, dân chúng nhìn lên | P+E | zig | medium |
| 143 | 11:27 | Ziggurat không chỉ là kiến trúc tôn giáo. Nó là một tuyên bố chính trị. Nó nói rằng thành phố này có thần bảo hộ, có kho lúa, có người tổ chức. | Wide: ziggurat như tuyên bố chính trị, cờ, kho | V+P | zig | wide |
| 144 | 11:35 | Nó nói rằng nơi đây không phải một đám dân du mục tụ tập. Nó là một trật tự. | Close: bóng ziggurat đổ lên nhà dân, trật tự | - | zig | close |
| 145 | 11:39 | Và trật tự đó cần một người đứng đầu. | Medium: Vua đứng trước ziggurat, đám đông cúi | V+E | zig | medium |
| 146 | 11:41 | Các vua Sumer không nói rằng mình được dân bầu. Họ nói rằng vương quyền từ trời xuống. Đó là một câu rất tiện. | Low: Vua giơ tay, vương quyền từ trời, mũ vàng | V | throne | low |
| 147 | 11:48 | Nếu quyền lực từ trời, thì chống lại vua là chống lại trời. | Close: bàn tay chỉ lên trời, bóng vua | V | throne | close |
| 148 | 11:51 | Nhưng các thành phố vẫn đánh nhau. Vì đất. Vì nước. Vì tuyến đường thương mại. Vì một vị thần của thành này muốn lấn sang thành khác. | Wide: hai thành phố đánh nhau, khói, tường | X | wall | wide |
| 149 | 11:59 | Trong lúc đánh nhau, họ vẫn trao đổi hàng hóa. Đồng từ Magan, có lẽ là Oman ngày nay. Thiếc từ phương đông. | Wide: thuyền chở đồng, thiếc, lapis cập bến | E | dock | wide |
| 150 | 12:05 | Đá lapis từ Afghanistan. Gỗ từ vùng núi phía bắc. Vải, gia vị, và có thể cả những ý tưởng. | Insert: lapis xanh, gỗ, vải, gia vị trên bàn | - | dock | insert |
| 151 | 12:11 | Để chở hàng. | Medium: bánh xe gỗ, trục, lừa | E | market | medium |
| 152 | 12:12 | Bánh xe không phát minh để đi xa. Nó ra đời để chở đất, chở lúa, chở người. Một bánh xe bằng gỗ ghép, viền đồng, gắn vào trục. | Close: bánh xe lăn trên đất, chở đất | E | market | close |
| 153 | 12:19 | Một con lừa kéo. Một người đứng sau. Tốc độ không nhanh hơn đi bộ. Nhưng nó chở được nhiều gấp nhiều lần. | Wide: lừa kéo xe, người đứng sau, chậm | E | field | wide |
| 154 | 12:25 | Cùng với bánh xe là cái cày. Cày bằng gỗ, đầu đồng, do lừa kéo. Một người có thể cày một mảnh ruộng mà trước đó cần vài người. | Medium: cày gỗ đầu đồng, lừa kéo, một người | N+E | field | medium |
| 155 | 12:32 | Năng suất tăng. Dân số tăng. Thành phố lại lớn hơn. | Wide: ruộng cày, dân số tăng, thành phố lớn | E | field | wide |
| 156 | 12:35 | Và bia. | Close: cốc bia, bọt, nắng | - | market | close |
| 157 | 12:36 | Ở Sumer, bia không phải thứ uống giải trí cuối tuần. Nó là khẩu phần. Bảng lương ghi cả lúa và bia. | Medium: Nông Dân nhận bia, bảng lương | N+S | market | medium |
| 158 | 12:42 | Một người lao động có thể nhận khoảng một đến hai lít bia mỗi ngày, tùy công việc. Bia nhẹ, an toàn hơn nước sông, và cung cấp calo. | Insert: bảng lương ghi lúa và bia, một đến hai lít | - | tablet | insert |
| 159 | 12:49 | Nó là thực phẩm, là tiền, là phần thưởng. | Wide: bia như thực phẩm, tiền, phần thưởng | E | market | wide |
| 160 | 12:52 | Hãy nhớ điều này, vì nó sẽ quay lại ở cuối câu chuyện. | Close: Tích giơ ngón tay, nhớ điều này | T | market | close |
| 161 | 12:55 | Đến khoảng năm 2334 trước Công nguyên, một người tên Sargon, xuất thân từ Akkad, phía bắc Sumer, làm một việc chưa ai làm được. | Wide: Sargon, người lạ từ Akkad, bóng lớn | V | wall | wide |
| 162 | 13:03 | Ông đánh chiếm từng thành phố Sumer, rồi giữ chúng lại dưới một chính quyền duy nhất. | Wide: lính Sargon cắm cờ trên cổng thành bị chiếm | X | wall | wide |
| 163 | 13:07 | Đó là một trong những đế chế đầu tiên trong lịch sử. | Map: bản đồ nhiều thành phố, một màu | - | abstract | top |
| 164 | 13:11 | Sargon không xóa người Sumer. Ông dùng họ. Ông đặt quan cai trị, thu thuế, xây dựng đường giao thông, và giữ tiếng Akkad làm ngôn ngữ hành chính. | Medium: Sargon và quan cai trị bên bảng thuế | V+S | throne | medium |
| 165 | 13:20 | Tiếng Sumer vẫn được nói, vẫn được viết, nhưng nó không còn là ngôn ngữ của quyền lực. | Close: Thư Lại viết lệnh Akkad bên bảng Sumer | S+E | tablet | close |
| 166 | 13:24 | Một thành phố có thể chọn vua. Một đế chế thì không. | Wide: một thành phố chọn vua, đế chế thì không | V | throne | wide |
| 167 | 13:27 | Và một khi đế chế xuất hiện, chiến tranh không còn là chuyện của hai thành phố. Nó là chuyện của cả một vùng đất. | Wide: chiến tranh cả vùng, bản đồ cháy | X | wall | wide |
| 168 | 13:34 | Sargon chết. Đế chế của ông giữ được khoảng hai thế kỷ rồi tan. Nhưng ý tưởng về đế chế thì không tan. | Medium: Sargon già bên bản đồ đế chế nứt | V | throne | medium |
| 169 | 13:40 | Một triều đại sau đó, Ur III, dựng lại một nhà nước tập trung ở miền nam. | Wide: Ur III, nhà nước tập trung, bảng kê | S+E | tablet | wide |
| 170 | 13:44 | Họ làm một việc mà chưa ai làm ở quy mô này: biến cả vùng đất thành một guồng máy kế toán. | Top: guồng máy kế toán, mũi tên, kho | - | abstract | top |
| 171 | 13:49 | Mỗi xưởng, mỗi đàn cừu, mỗi người thợ, mỗi chuyến hàng đều có bảng kê. Có những bảng ghi từng bữa ăn của từng người lao động. | Insert: bảng kê từng xưởng, đàn cừu, bữa ăn | S | tablet | insert |
| 172 | 13:57 | Nhà nước biết ai đang ở đâu, làm gì, ăn bao nhiêu. | Close: con dấu nhà nước trên bảng kê | V | tablet | close |
| 173 | 13:59 | Đó là lần đầu tiên trong lịch sử, một chính quyền cố gắng biết mọi thứ về mọi người. Và cũng là lần đầu tiên, con người có thể bị quản lý bằng giấy tờ. | Wide: con người bị quản lý bằng giấy tờ, hàng bảng | E | tablet | wide |

### Hồi 6. NGƯỜI KHÔNG CHẤP NHẬN CHẾT (14:08 đến 16:31)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 174 | 14:08 | Khoảng năm 2700 trước Công nguyên, có một vị vua ở Uruk. | Wide: Uruk 2700 TCN, tường thành, nắng | - | gate | wide |
| 175 | 14:12 | Tên ông được ghi lại là Gilgamesh. Chúng ta không biết chắc ông đã làm gì. | Medium: Gilgamesh trẻ, mũ, kiêu ngạo, bảng đất ghi tên | G | throne | medium |
| 176 | 14:16 | Nhưng chúng ta biết rằng, vài trăm năm sau, người ta kể về ông nhiều đến mức câu chuyện của ông trở thành một trong những tác phẩm văn học dài nhất còn lại từ thời cổ đại Lưỡng Hà. | Wide: thư viện bảng đất sét, bảng sử thi Gilgamesh ở tiền cảnh | S+E | tablet | wide |
| 177 | 14:27 | Sử thi Gilgamesh không bắt đầu bằng chiến công. Nó bắt đầu bằng một vị vua trẻ, mạnh, đẹp, và kiêu ngạo. | Medium: Gilgamesh đứng trên tường, dân làm việc | G+E | wall | medium |
| 178 | 14:33 | Ông xây tường thành, nhưng cũng bắt dân làm việc quá sức. Ông không sợ gì, vì ông chưa từng mất gì. | Close: bàn tay Gilgamesh siết, không sợ gì | G | wall | close |
| 179 | 14:39 | Rồi các thần tạo ra Enkidu, một người hoang dã, để đối đầu với ông. Hai người đánh nhau. Không ai thắng. Rồi họ trở thành bạn. | Wide: Gilgamesh và Enkidu vật nhau trong bụi, chưa phân thắng bại | G+K | myth | wide |
| 180 | 14:46 | Đây là điểm mà câu chuyện rẽ sang một hướng khác với mọi câu chuyện về anh hùng. | Medium: hai người ngồi cạnh nhau, câu chuyện rẽ | G+K | myth | medium |
| 181 | 14:50 | Gilgamesh và Enkidu đi giết Humbaba, con quái vật canh rừng tuyết tùng. Rồi họ giết cả bò thần do nữ thần Ishtar sai đến. Họ chiến thắng. Và rồi Enkidu chết. | Wide: Gilgamesh và Enkidu trước Humbaba, rừng tuyết tùng, bò thần gục | G+K+H+B | myth | wide |
| 182 | 15:00 | Không phải chết trong trận đánh. Chết vì bệnh. Chết vì các thần quyết định rằng phải có một người trả giá. | Close: Enkidu chết, bệnh, bàn tay buông | K | myth | close |
| 183 | 15:06 | Gilgamesh nhìn thấy bạn mình chết. Lần đầu tiên, ông hiểu rằng mình cũng sẽ chết. | Medium: Gilgamesh nhìn bạn chết, lần đầu hiểu | G | myth | medium |
| 184 | 15:10 | Và ông bắt đầu sợ. | Close: mắt Gilgamesh sợ, bóng tối | G | myth | close |
| 185 | 15:12 | Ông đi tìm người duy nhất biết bí mật của sự bất tử, Utnapishtim, người sống sót sau trận đại hồng thủy. | Wide: Gilgamesh đi tìm Utnapishtim, núi, biển | G | myth | wide |
| 186 | 15:18 | Ông đi qua núi, qua biển, qua vùng tối. Ông đến nơi. Ông hỏi. | Wide: Gilgamesh đi qua núi tối, biển đen, cửa hang | G | myth | wide |
| 187 | 15:22 | Utnapishtim nói với ông một điều rất đơn giản: không ai sống mãi. Các thần giữ sự sống cho riêng mình. Con người chỉ có cái chết. | Medium: Utnapishtim nói, không ai sống mãi | U+G | myth | medium |
| 188 | 15:29 | Nhưng vợ của Utnapishtim thương ông, và chỉ cho ông một loại cây mọc dưới đáy biển, có thể làm người già trẻ lại. | Close: bàn tay vợ Utnapishtim chỉ cây dưới đáy biển | F | myth | close |
| 189 | 15:35 | Gilgamesh lặn xuống, hái được cây. Trên đường về, ông dừng lại tắm. Một con rắn bò tới, ăn cây, và bỏ đi, để lại lớp da cũ. | Wide: Gilgamesh ướt sũng, cầm cây tiên trên bờ, rắn bò tới | G | myth | wide |
| 190 | 15:42 | Đó là lý do loài rắn lột da, và con người thì không. | Insert: rắn lột da, bò đi, da cũ | - | myth | insert |
| 191 | 15:46 | Gilgamesh trở về Uruk với hai bàn tay trắng. | Medium: Gilgamesh trở về, tay trắng, tường thành | G | wall | medium |
| 192 | 15:48 | Và đây là đoạn kết, có lẽ là đoạn kết hay nhất trong văn học cổ đại. | Wide: đoạn kết, bức tường, hoàng hôn | G | wall | wide |
| 193 | 15:53 | Ông không chết trong tuyệt vọng. Ông đứng trước bức tường thành của mình, và nói với người lái thuyền: hãy nhìn bức tường này. | Close: tay Gilgamesh chạm tường, nói với người lái thuyền | G | wall | close |
| 194 | 15:59 | Hãy sờ vào nó. Hãy xem nó được xây bằng gạch nung, kiên cố đến mức nào. | Insert: gạch nung, vữa, bàn tay | - | wall | insert |
| 195 | 16:04 | Ông không còn sự bất tử. Nhưng ông còn một thứ khác. | Medium: Gilgamesh nhìn thành phố, không bất tử | G | wall | medium |
| 196 | 16:07 | Ông còn thành phố. | Wide: thành phố Uruk, tường, người, khói | - | gate | wide |
| 197 | 16:08 | Câu chuyện về Gilgamesh được khắc lên đất sét. Nó được chép lại, truyền qua nhiều thế hệ, qua nhiều đế chế, qua nhiều ngôn ngữ. | Wide: thư lại đời sau chép lại bảng Gilgamesh, bảng cũ bên cạnh | S+E | tablet | wide |
| 198 | 16:15 | Phiên bản đầy đủ nhất mà chúng ta có được tìm thấy trong thư viện của vua Assyria Ashurbanipal, khoảng 700 năm trước Công nguyên. | Wide: thư viện Ashurbanipal, bảng xếp, đèn | S+E | tablet | wide |
| 199 | 16:23 | Một vị vua cố gắng bất tử bằng cách xây tường. | Medium: vua xây tường, bóng dài | V | wall | medium |
| 200 | 16:26 | Một người khác cố gắng bất tử bằng cách chép lại câu chuyện về ông. | Close: người chép lại, bút sậy, bảng | S | tablet | close |
| 201 | 16:30 | Người thứ hai thành công. | Close: Tích gật đầu, người thứ hai thành công | T | tablet | close |

### Hồi 7. MUỐI (16:31 đến 18:35)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 202 | 16:31 | Bây giờ hãy quay lại với thứ tôi đã nói ở đầu. | Medium: Tích quay lại, nhắc thứ đã nói ở đầu | T | salt | medium |
| 203 | 16:33 | Muối. | Close: muối trên tay, trắng, khô | - | salt | close |
| 204 | 16:34 | Nước sông ở đây không chỉ mang phù sa. Nó mang muối hòa tan, lấy từ đất và đá mà nó chảy qua. | Wide: sông mang muối, nước chảy qua đất đá | - | canal | wide |
| 205 | 16:40 | Khi bạn tưới ruộng, nước thấm xuống. Cây hút nước. Muối ở lại. | Insert: lát cắt đất, nước thấm xuống, muối đọng trắng | - | field | insert |
| 206 | 16:44 | Nếu đất có hệ thống thoát nước tự nhiên, muối bị rửa trôi. Nhưng ở Mesopotamia, đất bằng phẳng đến mức nước gần như không chảy đi đâu. | Wide: đồng bằng phẳng, nước gần như không thoát | - | field | wide |
| 207 | 16:51 | Kênh tưới đưa nước vào, nhưng nước ngầm dâng lên. Mực nước ngầm dâng đến gần mặt đất. Nước bốc hơi. Muối đọng lại thành một lớp trắng trên mặt ruộng. | Cutaway: kênh, nước ngầm, mặt ruộng trắng | - | field | wide |
| 208 | 16:59 | Nhìn từ xa, nó giống như sương muối. Nhìn gần, nó là cái chết. | Wide: ruộng trắng muối, cây chết khô | - | salt | wide |
| 209 | 17:03 | Lúa mì là loại cây nhạy cảm với muối. Lúa mạch chịu mặn tốt hơn. Nên khi đất bắt đầu mặn, người nông dân chuyển từ lúa mì sang lúa mạch. | Medium: Nông Dân cầm bó lúa mì và bó lúa mạch, ruộng trắng sau lưng | N | field | medium |
| 210 | 17:11 | Nhưng lúa mạch cũng có giới hạn. Đến một ngưỡng, không cây nào sống được. | Close: lúa mạch còi, đất trắng, ngưỡng chết | - | field | close |
| 211 | 17:16 | Các nhà nghiên cứu đã đọc được dấu vết này trong đất và trong các tấm bảng. Những cánh đồng ghi là tốt ở thế kỷ này, vài thế kỷ sau được ghi là bỏ hoang. | Insert: bảng đất hai cột, ruộng tốt và ruộng bỏ hoang | S | tablet | insert |
| 212 | 17:24 | Năng suất giảm dần, không phải vì lười, mà vì đất không còn nuôi được cây. | Wide: ruộng bỏ, người đi, thành phố vắng | - | field | wide |
| 213 | 17:29 | Đây là một trong những bài học sớm nhất, và vẫn còn đúng đến hôm nay: một nền văn minh có thể tự đầu độc nguồn đất của mình bằng chính thành tựu lớn nhất của nó. | Close: Tích nhìn ruộng mặn, tự đầu độc | T | salt | close |
| 214 | 17:38 | Nhưng muối không phải nguyên nhân duy nhất. | Medium: muối không phải nguyên nhân duy nhất, nền tối | - | salt | medium |
| 215 | 17:40 | Kênh bị phù sa lấp. Dòng sông đổi dòng. Chiến tranh phá hủy hệ thống tưới. Các bộ tộc từ phía tây tràn vào. | Wide: kênh bị phù sa lấp, bờ vỡ, thành phố xa | E | canal | wide |
| 216 | 17:47 | Thành phố bị cướp, bị đốt, bị bỏ. Mỗi thế kỷ, một chút ít. Không có một ngày tận thế nào cả. | Wide: thành phố cháy, tường đổ, người bỏ đi | X+E | gate | wide |
| 217 | 17:52 | Đế chế không sụp trong một trận đánh. Nó sụp trong từng mùa màng kém đi. | Close: mùa màng kém, từng hạt, không ngày tận thế | N | field | close |
| 218 | 17:56 | Đến khoảng năm 2000 trước Công nguyên, tiếng Sumer không còn là ngôn ngữ mẹ đẻ của ai. | Wide: đường vắng, bảng Sumer cuối cùng trên tường | - | gate | wide |
| 219 | 18:01 | Nó vẫn được dùng trong đền, trong trường học, trong văn bản pháp luật, giống như tiếng Latinh ở châu Âu thời Trung cổ. | Medium: đền, trường học, văn bản vẫn dùng tiếng Sumer | S | temple | medium |
| 220 | 18:08 | Nhưng ngoài đường, người ta nói tiếng Akkad, rồi tiếng Amorite, rồi những ngôn ngữ khác. | Wide: chợ đông, người Akkad và Amorite cạnh nhau | E | market | wide |
| 221 | 18:14 | Một nền văn minh chết không phải khi thành phố cuối cùng bị đốt. | Close: thành phố cuối cùng bị đốt, tường đổ | - | wall | close |
| 222 | 18:17 | Nó chết khi đứa trẻ cuối cùng không còn nói tiếng mẹ đẻ của nó. | Medium: đứa trẻ cuối cùng không nói tiếng mẹ đẻ | E | gate | medium |
| 223 | 18:20 | Câu chuyện đó không kết thúc ở Sumer. Miền nam Iraq ngày nay vẫn có đất bị mặn hóa. Đồng bằng sông Cửu Long cũng đang vật lộn với nước mặn xâm nhập. | Wide: ruộng muối nứt trắng, bờ biển và đồng bằng phía xa | - | salt | wide |
| 224 | 18:28 | Cùng một cơ chế: nước đến, muối ở lại. Chúng ta chỉ giỏi hơn ở chỗ gọi nó bằng một cái tên kỹ thuật và lập một ủy ban. | Close: Tích nhún vai, gọi tên kỹ thuật, lập ủy ban | T | salt | close |

### Hồi 8. DẤU VẾT CÒN LẠI (18:35 đến 20:55)

| # | Mốc | Lời kể | Hình | NV | Bối cảnh | Máy |
|---:|---|---|---|---|---|---|
| 225 | 18:35 | Nhưng có một điều kỳ lạ đã xảy ra. | Medium: Tích nhặt một mảnh bảng đất sét | T | ruins | medium |
| 226 | 18:37 | Đất sét không bền. Nó tan trong nước. Nếu để ngoài trời, một tấm bảng sẽ mềm ra và biến thành bùn sau vài trận mưa. | Insert: bảng mềm trong nước, tan thành bùn | - | tablet | insert |
| 227 | 18:44 | Nhưng đất sét đã nung thì thành đá. | Close: bảng nung cứng như đá, lửa | - | tablet | close |
| 228 | 18:46 | Nhiều tấm bảng Sumer còn đến hôm nay không phải vì ai đó cẩn thận cất giữ. Mà vì thành phố chứa chúng bị đốt. | Wide: thành phố cháy, bảng nằm dưới đổ nát | - | ruins | wide |
| 229 | 18:52 | Lửa thiêu rụi mọi thứ, nhưng nung cứng những tấm bảng. Chúng nằm dưới đống đổ nát hàng nghìn năm, chờ người đọc. | Insert: bảng trong tro, vẫn còn chữ | - | ruins | insert |
| 230 | 18:59 | Đến thế kỷ 19, các nhà khảo cổ châu Âu bắt đầu đào những gò đất ở Iraq. Họ tìm thấy hàng chục nghìn tấm bảng. | Wide: nhà khảo cổ đào gò đất, bảng xếp hàng | E | ruins | wide |
| 231 | 19:05 | Ban đầu không ai đọc được. Rồi từng người, từng người một, giải mã được chữ hình nêm. | Medium: người giải mã chữ nêm, từng dấu | - | study | medium |
| 232 | 19:10 | Một sĩ quan Anh tên Henry Rawlinson đã trèo lên một vách đá ở Behistun, chép lại ba thứ chữ khắc song song, và dùng chúng như chìa khóa. | Wide: Rawlinson trên vách đá Behistun, ba thứ chữ | R | ruins | wide |
| 233 | 19:18 | Khi chữ hình nêm được đọc, lịch sử không còn là truyền thuyết. Nó trở thành biên lai. | Close: chữ nêm thành biên lai, lịch sử | - | tablet | close |
| 234 | 19:23 | Một thế giới hiện ra: hợp đồng, thư từ, bài thơ, lời cầu nguyện, đơn kiện, thực đơn, bài tập của học trò. | Wide: hợp đồng, thư, thơ, đơn kiện xếp thành lớp | S | tablet | wide |
| 235 | 19:30 | Những tấm bảng đó nói với chúng ta nhiều hơn bất kỳ tượng đài nào. | Medium: bảng nói nhiều hơn tượng đài | T | ruins | medium |
| 236 | 19:33 | Và chúng ta vẫn đang dùng đồ của họ. | Close: đồng hồ trên tay Tích, sáu mươi phút | T | modern | close |
| 237 | 19:35 | Một giờ có 60 phút. Một phút có 60 giây. Một vòng tròn có 360 độ. | Insert: mặt đồng hồ, mười hai số, kim | - | modern | insert |
| 238 | 19:40 | Đó là hệ đếm cơ số 60 của người Sumer, được truyền qua Babylon, qua Hy Lạp, đến tận đồng hồ trên tay bạn. | Map: hệ đếm 60, Babylon, Hy Lạp, đồng hồ | - | abstract | top |
| 239 | 19:46 | Bánh xe. Cái cày. Thành phố có tường. Chữ viết. Luật thành văn. Trường học. Khái niệm nợ được ghi thành văn bản. | Wide: bánh xe, cày, tường, bảng chữ xếp như bảo tàng | E | abstract | wide |
| 240 | 19:53 | Tất cả đều bắt đầu ở đây, hoặc được ghi lại lần đầu ở đây. | Close: Tích gật đầu, tất cả bắt đầu ở đây | T | ruins | close |
| 241 | 19:56 | Nhưng có một thứ khác, ít được nhắc hơn. | Medium: một thứ khác, ít được nhắc hơn | T | ruins | medium |
| 242 | 19:59 | Người Sumer là những người đầu tiên ghi lại cảm giác rằng thế giới này không dành cho mình. Rằng mình sẽ chết. | Wide: người Sumer ghi cảm giác thế giới không dành cho mình | E | ruins | wide |
| 243 | 20:05 | Rằng thành phố mình xây sẽ đổ. Rằng nước mình dắt sẽ cạn. Rằng đất mình cày sẽ mặn. | Wide: thành phố đổ bên kênh cạn, đất trắng muối | - | ruins | close |
| 244 | 20:10 | Và họ vẫn tiếp tục xây. | Medium: họ vẫn xây, bàn tay trên gạch | N | wall | medium |
| 245 | 20:11 | Họ vẫn đào kênh. Vẫn nung gạch. Vẫn dạy trẻ con viết. | Wide: người đào kênh, người nung gạch, trẻ viết trong cùng một sân | E | canal | wide |
| 246 | 20:15 | Vẫn kể câu chuyện về một người đi tìm sự bất tử và trở về tay trắng, rồi đứng trước bức tường của mình và nói: hãy nhìn những gì ta đã làm. | Wide: kể chuyện Gilgamesh, tường, hãy nhìn | G+E | wall | wide |
| 247 | 20:23 | Ba mươi thế kỷ sau, chúng ta vẫn đứng trước những bức tường đó. | Wide: ba mươi thế kỷ sau, phế tích, Tích đứng | T | ruins | wide |
| 248 | 20:26 | Chúng không còn nguyên. Chúng chỉ là những gò đất cao, phủ đầy bụi, giữa một đồng bằng khô. | Close: gò đất phủ bụi, không còn nguyên | - | ruins | close |
| 249 | 20:32 | Nhưng mỗi lần bạn nhìn đồng hồ, chia một giờ thành sáu mươi phút, bạn đang đọc một dấu vết của họ. | Insert: đồng hồ, sáu mươi phút, dấu vết | T | ruins | insert |
| 250 | 20:37 | Mỗi lần bạn ký một hợp đồng, ghi một khoản nợ, bạn đang làm một việc mà một người Sumer đã làm trên một tấm đất sét, hơn năm nghìn năm trước. | Medium: Tích ký hợp đồng, ghi nợ, bảng đất sét | T | modern | medium |
| 251 | 20:45 | Và mỗi lần bạn xây một thứ gì đó, biết rằng nó sẽ không tồn tại mãi, bạn đang làm đúng việc mà họ đã làm. | Wide: Tích xây một thứ nhỏ, biết nó sẽ mất | T | plain | wide |
| 252 | 20:50 | Không phải vì bạn tin nó sẽ bền. | Close: Tích nhìn công trình, không phải vì bền | T | plain | close |
| 253 | 20:53 | Mà vì bạn tin nó đáng để xây. | Wide: Tích đứng trên đồng bằng, hoàng hôn, thành phố bắt đầu | T | plain | wide |

## 2. Nhân vật một lần

| Mã | Thiết kế | Dùng ở |
|---|---|---|
| G | Gilgamesh, vua trẻ Uruk, tóc đen xoăn, râu ngắn, mũ vàng, áo choàng da sư tử, thân hình cao hơn Vua một chút | 175 đến 201, 246 |
| K | Enkidu, người hoang, tóc dài rối, râu rậm, da thú, chân trần, cao bằng Gilgamesh | 179 đến 182 |
| U | Utnapishtim, già, râu trắng dài, áo trơn, mắt sâu, không đội mũ | 187 |
| H | Humbaba, mặt sư tử, bờm và râu cuộn, thân to, giữ rừng tuyết tùng | 181 |
| B | Bò thần, thân bò đen, sừng vàng, mắt đỏ, vòng cổ đồng | 181 |
| F | Vợ Utnapishtim, trung niên, tóc búi, áo trơn, tay chỉ | 188 |
| R | Henry Rawlinson, sĩ quan Anh thế kỷ 19, áo đỏ, mũ, râu quai nón | 232 |
| P | Tư tế, đầu cạo, mũ sừng nhỏ, áo lanh trắng, dây lapis | 62, 63, 64, 142, 143 |
| X | Lính, mũ đồng, khiên đan, giáo, áo da | 99, 137, 148, 162, 167, 216 |

H, B, F, R là thiết kế một lần, không nằm trong bốn bible chính. Khi chuyển sang prompt, vẫn dùng style lock và tỉ lệ đầu của bộ Sumer.

## 3. Nhịp cảnh

| Hồi | Beat | Thời lượng | Nhịp |
|---|---:|---:|---|
| 0 | 9 | 0:39 | chậm, giữ beat 1 thêm |
| 1 | 32 | 2:39 | đều, 4 đến 6 giây |
| 2 | 27 | 2:12 | đều, 4 đến 6 giây |
| 3 | 35 | 2:38 | đều, 4 đến 6 giây |
| 4 | 36 | 3:00 | đều, 4 đến 6 giây |
| 5 | 34 | 3:00 | đều, 4 đến 6 giây |
| 6 | 28 | 2:23 | chậm dần, nhiều khoảng trống |
| 7 | 23 | 2:05 | chậm dần, nhiều khoảng trống |
| 8 | 29 | 2:19 | chậm dần, nhiều khoảng trống |

## 4. Ghi chú dựng

- Beat 8 (0,62 giây) và beat 203 (1,05 giây) là hai lần chốt chữ Muối. Giữ hình ít nhất 1,5 đến 2 giây, không cắt ngay.
- Nếu nhập vào studio, hai beat này chỉ có một từ nên studio có thể chia rất ngắn. Gộp vào beat trước hoặc chỉnh tay khi dựng bằng studio.
- Đã cắt 5 cụm không có trong audio khỏi phụ đề và khỏi lời beat: beat 37 "Bạn xây lại lần nữa", beat 41 "Hãy quay lại với hai con sông", beat 50 "Bạn phải biết khi nào gieo", beat 87 "một ngày công đáng bao nhiêu lúa", beat 151 "họ cần bánh xe". Beat 151 còn 0,97 giây. Xem `sumer-retime-report.md`.
- Beat 110 là một danh sách. Cho chữ nêm chạy vào từng dòng, không cần diễn viên.
- Beat 179 đến 201 đổi palette sang thần thoại. Vẫn dùng cùng nét viền và cùng tỉ lệ đầu.
- Beat 236 đến 239 là cầu nối hiện đại. Đồng hồ, bánh xe, hợp đồng phải cùng nét với phần cổ.
- Beat 253 là ảnh cuối. Tích đứng trên đồng bằng, thành phố bắt đầu mọc phía sau, không chữ.
