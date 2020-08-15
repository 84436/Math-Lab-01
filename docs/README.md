# Lab 01 (Đồ án 1) "Color Compression"

**Môn:** `MTH00051` "Toán ứng dụng và thống kê" @ 18CLC4



---



## Sơ lược

Đồ án được viết bằng ngôn ngữ Python trên môi trường lập trình JupyterLab, sử dụng 03 thư viện bên ngoài: **Pillow/PIL** (đọc và ghi file ảnh), **NumPy** (tính toán) và **MatPlotLib** (xuất ảnh trên JupyterLab).

Mã nguồn đồ án này có 2 bản:

-   `ColorCompress.ipynb`: Notebook chính được dùng để viết và thử nghiệm chương trình
-   `ColorCompress_Batch.py`: Script chạy độc lập; xử lý hàng loạt thay vì đơn lẻ ảnh



## Về bản notebook

Phần bên dưới đây sẽ mô tả nội dung bên trong notebook.

-   Có 4 tham số đầu vào chính, được đặt tại code cell đầu tiên:
    -   `k_values`: tập các giá trị $k$
    -   `max_iterations`: số iteration tối đa có thể chạy
    -   `convergence_threshold`: ngưỡng hội tụ centroid
        
    -   `filename`: tên file ảnh cần xử lý
    
-   Về các thư viện (imports)

    -   `copy` được dùng để tạo một deep copy của tập centroid (sao lưu centroid trước khi chạy trong mỗi iteration)
    -   `time` được dùng để đo thời gian chạy của mỗi iteration (cụ thể hơn là hàm `time.perf_counter` được sử dụng.)

-   **Bước 1:** Tiền xử lý

    -   Ảnh sẽ được đọc vào (sử dụng `PIL.Image.open`) và lưu lại thành một mảng NumPy với kiểu dữ liệu là `float64`
    -   Tiếp đó, ảnh sẽ được reshape lại thành mảng 2 chiều `(width*height, 3)` – tức là mảng một chiều chứa các bộ 3 giá trị R/G/B tương ứng của mỗi điểm ảnh.

-   **Bước 2:** Giảm màu (sử dụng thuật toán $k$-means clustering)

    -   **Bước 2.1:** Lấy tập centroid là các điểm ảnh được chọn ngẫu nhiên <u>không trùng nhau về mặt giá trị</u> làm điểm bắt đầu
        -   `check = (random_pixel == centroids).all(1).any()`
            Với `random_pixel` là một điểm ảnh, và `centroids` là tập các điểm ảnh:
            -   Phép so sánh bằng `==` đầu tiên sẽ được NumPy thực hiện và trả về một mảng NumPy chứa giá trị so sánh giữa từng phần tử một trong `random_pixel` với phần tử tương ứng trong mỗi điểm ảnh trong `centroids`
            -   `.all(axis=1)` sẽ "thực hiện phép AND" trên từng bộ ba giá trị có được trong mảng kết quả trên
            -   `.any()` sẽ "thực hiện phép OR" trên từng giá trị có được trong mảng kết quả trên nữa. Bước cuối này sẽ là bước trả lời cho câu "`random_pixel` đã tồn tại trong `centroids` hay chưa?"
    -   **Bước 2.2:** Label từng điểm ảnh
        -   Với mỗi điểm ảnh, so sánh khoảng cách với từng centroid trong tập centroid hiện tại (`numpy.linalg.norm`) và chọn ra khoảng cách nhỏ nhất (`numpy.argmin`)
    -   **Bước 2.3**: Cập nhật tập centroid: Với từng centroid hiện tại…
        -   `point_labels = image[labels == label]`
            Lọc ra những điểm ảnh có label tương ứng với centroid đã chọn.
            *(Phần `[labels == label]` là một cú pháp đặc biệt để lọc mảng trong NumPy dựa trên một phép so sánh)*
        -   `centroids[label] = np.mean(point_labels, axis=0)`
            Tính trung bình giá trị trên cả tập điểm ảnh trên, sau đó gán thành một centroid mới thay thế centroid cũ ("cập nhật centroid").
    -   Mỗi một lần chạy bước 2.2 và bước 2.3 được gọi là một *iteration*. Trước khi bắt đầu mỗi một iteration, tập centroid hiện tại sẽ được sao lưu vào `last_known_centroids` để so sánh.
    -   **Điều kiện dừng:** Bước 2.2 và 2.3 được lặp lại cho đến khi một trong 2 điều kiện sau xảy ra:
        -   <u>Tập centroid đã hội tụ</u>: Nếu sự sai khác giữa từng thành phần trong 2 tập centroid (trước và sau mỗi iteration) bé hơn `convergence_threshold` đã được định nghĩa từ đầu, 2 tập centroid được xem là bằng nhau. Phép kiểm tra này được thực hiện bằng `numpy.allclose`.
        -   <u>Số iterations đến hiện tại đã chạm mức</u> `max_iteration`

-   **Bước 3:** Hậu xử lý
    Như comment được để lại trong notebook, bước này thực hiện các công việc sau:
    - Làm tròn các giá trị trong centroid (để map trực tiếp qua mã màu R/G/B; giá trị của các điểm ảnh lúc import vào và sau khi xử lý đều là `float64`)
    - Dựng lại ảnh (map từng giá trị trong label với centroid tương ứng, sau đó reshape lại thành ảnh có kích thước gốc)
    - Hiện ảnh (bằng **MatPlotLib**) + ghi ảnh ra file



## Về bản script

Mã nguồn trong script tương tự như bản notebook, với **3** điểm khác biệt:

-   Thư viện **MatPlotLib** không được sử dụng
-   3 bước chính (tiền xử lý – giảm màu – hậu xử lý) được gói lại thành một hàm để có thể xử lý hàng loạt: lấy tất cả ảnh ra trong `input`, đưa vào hàm với các tham số cần thiết và trả ra `output` với định dạng tên file là `<tên file gốc>_<số k>.jpg`.
-   `input` sẽ không chấp nhận xử lý những file ảnh có đuôi khác `.jpg`[^1]



### Để chạy script…

1.  *(Không bắt buộc)* Xóa toàn bộ file trong `output` (nhưng không xóa thư mục `output` chính nó) và thêm/bớt ảnh trong `input` nếu cần.
2.  *(Không bắt buộc)* Chỉnh sửa các tham số được đặt ở đầu file dựa theo mô tả tham số trong bản notebook nếu cần thiết, kèm theo đó:
    -   `input_basepath`, `output_basepath`: thư mục input và output tương ứng (cần phải tồn tại trước khi chạy)
3.  Chạy: `python ColorCompress_Batch.py`



### Output mẫu

Dưới đây là output của `ColorCompress_Batch.py` trên tập input kèm sẵn. Các file ảnh input và output tương ứng với lần chạy mẫu này được kèm trong thư mục `output` của đồ án này.

Mỗi một dòng, trừ dòng đầu tiên (chỉ định số file input thấy được), đều theo định dạng:

```
<tên file> k=<giá trị k> t=<thời gian xử lý> i=<số iteration>
```

với `<thời gian xử lý>` là tổng thời gian từ lúc đọc file ảnh cho đến lúc xuất file ảnh đã được xử lý.

```
10 input file(s)
animal_cate.jpg k=3 t=1.55s i=9
animal_cate.jpg k=5 t=4.40s i=26
animal_cate.jpg k=7 t=6.00s i=28
animal_tom.jpg k=3 t=2.27s i=8
animal_tom.jpg k=5 t=3.95s i=12
animal_tom.jpg k=7 t=5.83s i=14
color_ballons.jpg k=3 t=3.11s i=29
color_ballons.jpg k=5 t=5.27s i=35
color_ballons.jpg k=7 t=2.37s i=10
color_glass_rainbow.jpg k=3 t=4.87s i=15
color_glass_rainbow.jpg k=5 t=10.79s i=27
color_glass_rainbow.jpg k=7 t=6.08s i=11
color_glass_sunmoon.jpg k=3 t=1.75s i=9
color_glass_sunmoon.jpg k=5 t=1.93s i=7
color_glass_sunmoon.jpg k=7 t=9.43s i=38
color_tvtest.jpg k=3 t=1.85s i=6
color_tvtest.jpg k=5 t=2.08s i=5
color_tvtest.jpg k=7 t=3.01s i=7
landscape_baucacai.jpg k=3 t=2.15s i=7
landscape_baucacai.jpg k=5 t=3.72s i=11
landscape_baucacai.jpg k=7 t=4.27s i=10
landscape_bliss.jpg k=3 t=1.01s i=6
landscape_bliss.jpg k=5 t=1.39s i=7
landscape_bliss.jpg k=7 t=3.17s i=16
landscape_darcy_ertman.jpg k=3 t=2.34s i=11
landscape_darcy_ertman.jpg k=5 t=3.36s i=12
landscape_darcy_ertman.jpg k=7 t=11.78s i=39
landscape_desert.jpg k=3 t=2.06s i=9
landscape_desert.jpg k=5 t=2.45s i=8
landscape_desert.jpg k=7 t=4.55s i=14
```



---



[^1]: Mục đích của việc này là để tránh những ảnh PNG có 4 kênh màu (R/G/B/A) thay vì 3 kênh (R/G/B), nhưng cách làm này dẫn đến 2 nhược điểm: (a.) những định dạng ảnh khác mà vẫn đảm bảo 3 kênh màu (VD: Bitmap, `GIF`, v.v.) cũng sẽ không được chấp nhận, và (b.) đây là dấu hiệu của việc code chưa chuẩn :<