import bigbrother

# simple subscriber to imu and log using rerun
import rclpy
from rclpy.node import Node
from booster_interface.msg import LowState, BatteryState

class Diag(Node):
    def __init__(self):
        super().__init__('diag')
        self.low_state_subscription = self.create_subscription(
            LowState,
            '/low_state',
            self.low_state_callback,
            10)
        
        self.battery_subscription = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            10)

    def low_state_callback(self, msg):
        bigbrother.log_booster_joint_states(msg.motor_state_parallel)
    
        bigbrother.log_imu_data(msg.imu_state.rpy[0], msg.imu_state.rpy[1], msg.imu_state.rpy[2])

    def battery_callback(self, msg):
        bigbrother.log_battery_voltage(msg.voltage, msg.current)

def main(args=None):
    rclpy.init(args=args)
    diag = Diag()
    rclpy.spin(diag)
    diag.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()



# ---
# imu_state:
#   rpy:
#   - 0.0026356233283877373
#   - 0.34956878423690796
#   - -2.7773208618164062
#   gyro:
#   - 0.000774065381847322
#   - 0.00016008541570045054
#   - 0.0005209230002947152
#   acc:
#   - -3.3443398475646973
#   - 0.006573404185473919
#   - 9.190568923950195
# motor_state_parallel:
# - mode: 0
#   q: 0.0
#   dq: 4.359507147455588e-05
#   ddq: 0.0
#   tau_est: -0.010850000195205212
#   temperature: 51
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.774088442325592
#   dq: 0.0018386320443823934
#   ddq: 0.0
#   tau_est: -0.14788000285625458
#   temperature: 51
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.007670138031244278
#   dq: 0.001768868532963097
#   ddq: 0.0
#   tau_est: 0.0012817773967981339
#   temperature: 48
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.6651870012283325
#   dq: 0.00483419606462121
#   ddq: 0.0
#   tau_est: -0.0038453321903944016
#   temperature: 45
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.02416093461215496
#   dq: 0.0003134989528916776
#   ddq: 0.0
#   tau_est: -0.0012817773967981339
#   temperature: 42
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.794428825378418
#   dq: -0.02008957788348198
#   ddq: 0.0
#   tau_est: 0.0029908139258623123
#   temperature: 39
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.061361104249954224
#   dq: 0.006698002107441425
#   ddq: 0.0
#   tau_est: 0.01196325570344925
#   temperature: 51
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 1.3840763568878174
#   dq: 0.007642339915037155
#   ddq: 0.0
#   tau_est: 0.01837214268743992
#   temperature: 46
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.046404335647821426
#   dq: -0.004530742298811674
#   ddq: 0.0
#   tau_est: -0.0008545182645320892
#   temperature: 45
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 1.3875279426574707
#   dq: -0.0013736214023083448
#   ddq: 0.0
#   tau_est: 0.01580858789384365
#   temperature: 41
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.9625009298324585
#   dq: -0.0036151872482150793
#   ddq: 0.0
#   tau_est: 0.06981685012578964
#   temperature: 52
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.1188296303153038
#   dq: -0.005461555905640125
#   ddq: 0.0
#   tau_est: 0.32293039560317993
#   temperature: 46
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.01125352829694748
#   dq: -0.0003619629715103656
#   ddq: 0.0
#   tau_est: 0.08051282167434692
#   temperature: 43
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.023460745811462402
#   dq: -0.003928238991647959
#   ddq: 0.0
#   tau_est: -0.029084250330924988
#   temperature: 38
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.31834134459495544
#   dq: -0.0009474484832026064
#   ddq: 0.0
#   tau_est: 0.2875458002090454
#   temperature: 38
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.12340734153985977
#   dq: -0.0031846093479543924
#   ddq: 0.0
#   tau_est: 0.01150183193385601
#   temperature: 37
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.9720377922058105
#   dq: 0.00039926316821947694
#   ddq: 0.0
#   tau_est: 0.06981685012578964
#   temperature: 47
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.19130998849868774
#   dq: -0.009583908133208752
#   ddq: 0.0
#   tau_est: 0.15296703577041626
#   temperature: 49
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.04940108209848404
#   dq: 0.005345909856259823
#   ddq: 0.0
#   tau_est: 0.31054946780204773
#   temperature: 43
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.0020981156267225742
#   dq: -0.0001461310894228518
#   ddq: 0.0
#   tau_est: 0.029084250330924988
#   temperature: 39
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.2283131182193756
#   dq: -0.0006914847763255239
#   ddq: 0.0
#   tau_est: 0.01150183193385601
#   temperature: 41
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.2744716703891754
#   dq: -0.016094576567411423
#   ddq: 0.0
#   tau_est: 0.10351648926734924
#   temperature: 38
#   lost: 0
#   reserve:
#   - 0
#   - 0
# motor_state_serial:
# - mode: 0
#   q: 0.0
#   dq: 4.359507147455588e-05
#   ddq: 0.0
#   tau_est: -0.010850000195205212
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.774088442325592
#   dq: 0.0018386320443823934
#   ddq: 0.0
#   tau_est: -0.14788000285625458
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.007670138031244278
#   dq: 0.001768868532963097
#   ddq: 0.0
#   tau_est: 0.0012817773967981339
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.6651870012283325
#   dq: 0.00483419606462121
#   ddq: 0.0
#   tau_est: -0.0038453321903944016
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.02416093461215496
#   dq: 0.0003134989528916776
#   ddq: 0.0
#   tau_est: -0.0012817773967981339
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.794428825378418
#   dq: -0.02008957788348198
#   ddq: 0.0
#   tau_est: 0.0029908139258623123
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.061361104249954224
#   dq: 0.006698002107441425
#   ddq: 0.0
#   tau_est: 0.01196325570344925
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 1.3840763568878174
#   dq: 0.007642339915037155
#   ddq: 0.0
#   tau_est: 0.01837214268743992
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.046404335647821426
#   dq: -0.004530742298811674
#   ddq: 0.0
#   tau_est: -0.0008545182645320892
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 1.3875279426574707
#   dq: -0.0013736214023083448
#   ddq: 0.0
#   tau_est: 0.01580858789384365
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.9625009298324585
#   dq: -0.0036151872482150793
#   ddq: 0.0
#   tau_est: 0.06981685012578964
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.1188296303153038
#   dq: -0.005461555905640125
#   ddq: 0.0
#   tau_est: 0.32293039560317993
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.01125352829694748
#   dq: -0.0003619629715103656
#   ddq: 0.0
#   tau_est: 0.08051282167434692
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.023460745811462402
#   dq: -0.003928238991647959
#   ddq: 0.0
#   tau_est: -0.029084250330924988
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.2488965541124344
#   dq: 0.002381102181971073
#   ddq: 0.0
#   tau_est: -0.28490257263183594
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.14695635437965393
#   dq: -0.0021515903063118458
#   ddq: 0.0
#   tau_est: -0.17164906859397888
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -1.9720377922058105
#   dq: 0.00039926316821947694
#   ddq: 0.0
#   tau_est: 0.06981685012578964
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.19130998849868774
#   dq: -0.009583908133208752
#   ddq: 0.0
#   tau_est: 0.15296703577041626
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.04940108209848404
#   dq: 0.005345909856259823
#   ddq: 0.0
#   tau_est: 0.31054946780204773
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: -0.0020981156267225742
#   dq: -0.0001461310894228518
#   ddq: 0.0
#   tau_est: 0.029084250330924988
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.29421865940093994
#   dq: 0.010808826424181461
#   ddq: 0.0
#   tau_est: -0.09963947534561157
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# - mode: 0
#   q: 0.04987194389104843
#   dq: 0.012365620583295822
#   ddq: 0.0
#   tau_est: -0.048280760645866394
#   temperature: 0
#   lost: 0
#   reserve:
#   - 0
#   - 0
# ---