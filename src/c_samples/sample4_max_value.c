#include <stdio.h>

// Ví dụ 4: Tìm số lớn nhất
// Lỗi: Khởi tạo sai
int main() {
    int arr[] = {3, 7, 2, 9, 1};
    int n = 5;
    int max = 0;  // BUG: Nên khởi tạo là arr[0] hoặc INT_MIN
    
    for (int i = 0; i < n; i++) {
        if (arr[i] > max) {
            max = arr[i];
        }
    }
    
    printf("Max: %d\n", max);
    // Nếu tất cả phần tử đều âm, kết quả sẽ sai
    return 0;
}

/* SỬA:
int max = arr[0];
// hoặc
#include <limits.h>
int max = INT_MIN;
*/
