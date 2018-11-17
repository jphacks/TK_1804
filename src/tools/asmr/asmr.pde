import processing.opengl.*;
import processing.net.*;

int port = 10001; // 適当なポート番号を設定

Server server;
Client client;
JSONObject json;

ProjectionVector pv;
Speaker sp[];

float th[];
color noSwitch;
color leftSwitch;
color rightSwitch;
color spstatus[];

float body_line_size = 5;
float other_line_size = 2;

float input_vector_size = 300;
float projection_vector_size = 400;

void setup() {
  size(700, 1000, OPENGL);
  background(255, 255, 255);
  pv = new ProjectionVector(0, 0, 100);

  sp = new Speaker[5];
  for(int i=0; i<sp.length - 1; i++) {
    sp[i] = new Speaker(60*i, 180);
  }
  sp[sp.length-1] = new Speaker(270, 100);
  
  th = new float[4];
  for(int i=0; i<th.length; i++)
  {
    th[i] = cos(radians(i*60));
  }
  
  noSwitch = color(155, 155, 155);
  rightSwitch = color(255, 100, 50);
  leftSwitch = color(50, 220, 255);
  
  spstatus = new color[5];
  for(int i=0; i<spstatus.length; i++) {
    spstatus[i] = noSwitch;
  }
  
  server = new Server(this, port);
  println("server address: " + server.ip()); // IPアドレスを出力
  client = server.available();
}

void draw() {
  
  background(255, 255, 255);
  
   try {
     client = server.available();
     if (client !=null) {
        String whatClientSaid = client.readString();
        if (whatClientSaid != null) {
          json = parseJSONObject(whatClientSaid);
          pv.x = json.getFloat("x");
          pv.y = json.getFloat("y");
          pv.z = json.getFloat("z"); 
        }  
      }
  } catch(NullPointerException e) {  
      println("clinet is un available");  
  }

  pv.setVectorSize(input_vector_size);

  for(int i=0; i<spstatus.length; i++) {
    spstatus[i] = noSwitch;
  }

  pushMatrix();
  //rotateZ(radians(180));
  // ビューポイントの移動
  translate(width/2, height/2, 0);
  rotateX(radians(70));
  rotateZ(radians(20));
  
  // x, y, z軸の直線
  stroke(0, 0, 0);
  line(-width, 0, 0, width, 0, 0);
  line(0, -height*2, 0, 0, height, 0);
  line(0, 0, -1000, 0, 0, 1000);
  
  // 元のベクトル 赤
  stroke(255, 0, 0);
  strokeWeight(body_line_size);
  //line(0, 0, 0, pv.x, pv.y, pv.z);
  
  // 射影ベクトル 緑
  stroke(0, 255, 0);
  strokeWeight(body_line_size);
  pv.projection(projection_vector_size);
  line(0, 0, 0, pv.c_p_x, 0, pv.c_p_z);
  
  // 左耳
  stroke(leftSwitch);
  strokeWeight(body_line_size);
  pv.leftEarVector();
  line(0, 0, 0, pv.l_e_x, 0, pv.l_e_z);
  
  // 右耳
  stroke(rightSwitch);
  strokeWeight(body_line_size);
  pv.rightEarVector();
  line(0, 0, 0, pv.r_e_x, 0, pv.r_e_z);
  
  strokeWeight(other_line_size);
  // 左耳の判定
  checkOnSpeaker(spstatus, pv.l_e_x, pv.l_e_z, th, leftSwitch);
  checkOnSpeaker(spstatus, pv.r_e_x, pv.r_e_z, th, rightSwitch);
  
  for(int i=0; i<sp.length; i++) {
    stroke(spstatus[i]);
    sp[i].drawSpeaker();
  }
  
  popMatrix();
}

color setAlpha(color c, float per) {
  return color(red(c), green(c), blue(c), (int)(255*per));
}
void checkOnSpeaker(color spstatus[], float vec_x, float vec_z, float th[], color spSwitch) {
  float cos = vec_x / sqrt(pow(vec_x, 2) + pow(vec_z, 2));
  float theta = acos(cos);
  float comp_1 = 0;
  float comp_2 = 0;
  if(vec_z < 0) {
    theta = 2*PI - theta;
    if (vec_x == 0) {
      spstatus[4] = setAlpha(spSwitch, 1);
    }else if (vec_x > 0) {
      comp_1 = radians(270);
      comp_2 = radians(360);
      comp_1 = abs(theta - comp_1);
      comp_2 = abs(theta - comp_2);
      spstatus[0] = setAlpha(spSwitch, comp_1/(comp_1 + comp_2));
      spstatus[4] = setAlpha(spSwitch, comp_2/(comp_1 + comp_2));
    } else if (vec_x < 0) {
      comp_1 = radians(180);
      comp_2 = radians(270);
      comp_1 = abs(theta - comp_1);
      comp_2 = abs(theta - comp_2);
      spstatus[3] = setAlpha(spSwitch, comp_2/(comp_1 + comp_2));
      spstatus[4] = setAlpha(spSwitch, comp_1/(comp_1 + comp_2)); 
    }
  } else {
    int i = 0;
    for(i = 0; i< th.length; i++){
      if (th[i] == cos) {
        spstatus[i] = setAlpha(spSwitch, 1);
        break;
      }else if(th[i] < cos) {
        comp_1 = radians((i - 1) * 60);
        comp_2 = radians(i * 60);
        comp_1 = abs(theta - comp_1);
        comp_2 = abs(theta - comp_2);
        spstatus[i - 1] = setAlpha(spSwitch, comp_2/(comp_1 + comp_2));
        spstatus[i] = setAlpha(spSwitch, comp_1/(comp_1 + comp_2));
        break;
      }
    }
  }
}

class InputVector {

  public float x;
  public float y;
  public float z;
  
  InputVector(float _x, float _y, float _z) {
    this.x = _x;
    this.y = _y;
    this.z = _z;
  }
  
  public float vectorSize() {
    return sqrt(pow(this.x, 2) + pow(this.y, 2) + pow(this.z, 2));
  }
  
  public void setVectorSize(float size) {
    float vectorSize = this.vectorSize();
    this.x = (this.x / vectorSize) * size;
    this.y = (this.y / vectorSize) * size;
    this.z = (this.z / vectorSize) * size;
  }
  
  public void moveHead(float _x, float _y, float _z) {
    this.x = _x;
    this.y = _y;
    this.z = _z;
  }

}

class ProjectionVector extends InputVector {

  public float c_p_x;
  public float c_p_z;
  
  public float b_p_x;
  public float b_p_z;
  
  public float l_e_x;
  public float l_e_z;
  
  public float r_e_x;
  public float r_e_z;
  
  public float threthold;
  
  public float get_c_p_x() {
    return this.c_p_x;
  }
  public float get_c_p_z() {
    return this.c_p_z;
  }
  
  ProjectionVector(float _x, float _y, float _z){
    super(_x, _y, _z);
    projection(500);
    this.b_p_x = 0;
    this.b_p_z = 1;
    this.threthold = radians(1);
  }
  
  public void projection(float size) {
    //float parametor = sqrt(1-pow(y/this.vectorSize(), 2));
    this.c_p_x = this.x;
    this.c_p_z = this.z;

    float vectorSize = ProjectionVectorSize(this.c_p_x, this.c_p_z);
    this.c_p_x = this.c_p_x / vectorSize * size;
    this.c_p_z = this.c_p_z / vectorSize * size;
 
  }
  
  public float ProjectionVectorSize(float x, float z) {
    return sqrt(pow(x, 2) + pow(z, 2));
  }
  
  public float getDiffTheta() {
    float dot = ((this.c_p_x * this.b_p_x) + (this.c_p_z * this.b_p_z)) / (ProjectionVectorSize(this.c_p_x, this.c_p_z) * ProjectionVectorSize(this.b_p_x, this.b_p_z));
    if (dot > 1) dot = 1;
    float theta = acos(dot);
    
    float BcrosA = this.b_p_z * this.c_p_x - this.b_p_x * this.c_p_z;
    
    if (BcrosA >= 0) theta = -1 * theta;
    
    return theta;
  }
  
  public void leftEarVector() {
    this.l_e_x = this.c_p_z * -1;
    this.l_e_z = this.c_p_x;
  }
  
  public void rightEarVector() {
    this.r_e_x = this.c_p_z;
    this.r_e_z = this.c_p_x * -1;
  }
}

class Speaker{
  float x;
  float z;
  float sr;
  
  Speaker(float angle, float _r){
    this.x = _r * cos(radians(angle));
    this.z = _r * sin(radians(angle));
    this.sr = 20;
  }
  
  public void drawSpeaker() {
    pushMatrix();
    translate(this.x, 0, this.z);
    sphere(this.sr);
    popMatrix();
  }
}

float a = 10;
void keyPressed() {
  if (key == '-') {
    a = -10;
  }
  if (key == 'j') {
    pv.x += a;// コード化されているキーが押された
  } else if (key == 'k') {
    pv.y += a;
  } else if (key == 'l') {
    pv.z += a;
  }
}

void keyReleased() {
  if (key == '-') {
    a = 10;
  }
}
