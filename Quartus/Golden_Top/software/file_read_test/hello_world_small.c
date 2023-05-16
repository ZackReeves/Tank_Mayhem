#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#define BUF_SIZE (50)

int main()
{

           FILE* fp_ascii = NULL;
           char buffer[BUF_SIZE];
           int read_size, i;

           fp_ascii = fopen ("comand.txt", "r");
           if (fp_ascii == NULL)
           {
             alt_printf ("cannot open file for reading\n");
             exit();
           }

          fgets(buffer, sizeof(buffer), fp_ascii);
          alt_printf("%s", buffer);
          fclose(fp_ascii);

}
