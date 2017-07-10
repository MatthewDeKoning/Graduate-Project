data = csvread('V.csv');
[x,y] = size(data);

distance = data(1:7:y*x);
width = data(2:7:y*x);
velocity = data(3:7:y*x);
w_est = data(4:7:y*x);
w_err = data(5:7:y*x);
v_est = data(6:7:y*x);
v_err = data(7:7:y*x);
figure();
scatter(velocity, v_err);
xlabel('Velocity');
ylabel('Velocity Error (ft/s)');
