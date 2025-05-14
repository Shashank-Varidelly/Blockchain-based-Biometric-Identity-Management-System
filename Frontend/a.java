import java.util.*;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
class a{
	public static void main(String args[]){
		BufferedReader br=new BufferedReader(new InputStreamReader(System.in));
		try{
			String l=br.readLine();
			int n=Integer.parseInt(l);
			ArrayList<String> as=new ArrayList<>();
			for(int i=0;i<n;i++){
		StringBuilder str=br.readLine();
		as.add(str.toString());
		str.setLength(0);
			}
			for(String st:as){
				System.out.println(test(st));
			}
		
		
		}catch(Exception e){
			System.out.println("incorrect input");
		}
	}
	
	public static int test(String st){
		ArrayList<Integer> al=new ArrayList<>();
		int arr[]=new int[3];
		StringBuilder sb=new StringBuilder();
		for(int i=0;i<str.length();i++){
			char c=str.charAt(i);
			if(Character.isDigit(c)){
				sb.append(c);
			}else if(sb.length()>0){
				al.add(Integer.parseInt(sb.toString()));
				sb.setLength(0);
			}
		}
		if(sb.length()>0){
				al.add(Integer.parseInt(sb.toString()));
				sb.setLength(0);
			}
		
		int i=0;
		for(int num:al){
			arr[i]=num;
			
			i++;
		}
		Arrays.sort(arr);
		int f=arr[0];
		int s=arr[1];
		int t=arr[2];
		if(f==s && f==t){
			return 0;
		}
		int count=0;
		if(f==s){
		while(f<=s && f<=t){
			if(f==s && f==t){
				return count;
			}else {
				f++;
				s++;
				t--;
				count++;
			}
		}
		}
		else if(s==t){
			while(f<=s && f<=t){
			if(f==s && f==t){
				return count;
			}else {
				f++;
				s--;
				t--;
				count++;
			}
		}
			
		}
		return -1;
	}
}